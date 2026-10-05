"""Pure declared-parent/sticky predicates, never actual removal authorization."""

import json
import re

MAX_INPUT_BYTES = 16_384
MAX_OUTPUT_BYTES = 65_536
MAX_DEPTH = 6
MAX_NUMERIC_CHARS = 10
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,31}", re.ASCII)
CONTEXT = {
    "identity_mapping": ("assumed_identity", "other", "unknown"),
    "parent_permission_source": ("declared_ordinary_bits", "acl", "unknown"),
    "ancestor_search": ("assumed_satisfied", "not_satisfied", "unknown"),
    "privilege": ("ordinary_no_capabilities", "capabilities", "unknown"),
    "entry_state": ("assumed_existing", "missing", "unknown"),
}
FEATURES = frozenset(("acl", "lsm", "readonly", "append_only", "immutable", "swapfile",
                      "mountpoint", "idmap", "namespace", "symlink", "race", "remote_fs",
                      "descriptor", "default_inheritance", "unknown_context"))
ASSUMPTIONS = ("invented_filesystem_ids", "identity_mapping_assumed",
               "declared_parent_access", "declared_context_only")
NOT_VERIFIED = ("actual_unlink", "entry_removed", "storage_reclaimed", "input_truth",
                "parent_access_selection", "ancestor_search", "full_system_policy")


class _Invalid(ValueError):
    def __init__(self, reason: str, status: str = "rejected"):
        self.reason, self.status = reason, status


def _outcome(status: str, reason: str) -> dict:
    return {"status": status, "complete": status == "model_complete", "reason": reason,
            "actual_unlink": "unverified", "entry_removed": "unverified", "storage_reclaimed": "unverified",
            "assumptions": list(ASSUMPTIONS), "not_verified": list(NOT_VERIFIED)}


def _keys(value: object, expected: set[str]) -> dict:
    if type(value) is not dict or len(value) != len(expected):
        raise _Invalid("object_shape")
    # Identity admission before input-key hash/equality; no metaclass equality.
    if any(type(key) is not str or len(key) > 32 for key in value) or set(value) != expected:
        raise _Invalid("object_shape")
    return value


def _integer_value(value: object, maximum=999_999_999) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise _Invalid("integer_range")
    return value


def _identifier(value: object) -> str:
    if type(value) is not str or len(value) > 32 or IDENTIFIER.fullmatch(value) is None:
        raise _Invalid("identifier")
    return value


def _enum(value: object, choices: tuple | frozenset) -> str:
    if type(value) is not str or len(value) > 32 or value not in choices:
        raise _Invalid("enum")
    return value


def _validated(value: object) -> tuple:
    record = _keys(value, {"id", "version", "profile", "operation", "subject", "parent", "target", "context"})
    label, version, profile = _identifier(record["id"]), _integer_value(record["version"]), _identifier(record["profile"])
    operation = _enum(record["operation"], ("unlink_regular", "rename_regular", "replace_regular"))
    subject = _keys(record["subject"], {"fsuid"})
    fsuid = _integer_value(subject["fsuid"])
    parent = _keys(record["parent"], {"owner_uid", "declared_access_bits", "sticky"})
    parent_uid, bits = _integer_value(parent["owner_uid"]), _integer_value(parent["declared_access_bits"], 7)
    sticky = parent["sticky"]
    if type(sticky) is not bool:
        raise _Invalid("boolean_type")
    target = _keys(record["target"], {"owner_uid", "kind", "content_bits"})
    target_uid = _integer_value(target["owner_uid"])
    kind = _enum(target["kind"], ("regular", "directory", "symlink", "other", "unknown"))
    content = _integer_value(target["content_bits"], 7)
    context = _keys(record["context"], {*CONTEXT, "excluded_features"})
    declarations = tuple((field, _enum(context[field], choices)) for field, choices in CONTEXT.items())
    features = context["excluded_features"]
    if type(features) is not list:
        raise _Invalid("list_shape")
    if len(features) > 16:
        raise _Invalid("list_limit", "over_limit")
    features = tuple(_enum(feature, FEATURES) for feature in features)
    if len(set(features)) != len(features):
        raise _Invalid("duplicate_feature")
    # Full current common validation precedes every exclusion or bit decision.
    unsupported = [f"{field}_{declaration}" for field, declaration in declarations if declaration != CONTEXT[field][0]]
    unsupported.extend(f"feature_{feature}" for feature in features)
    for reason, condition in (("version", version != 1), ("profile", profile != "sticky_unlink_v1"),
                              ("fsuid_zero", fsuid == 0)):
        if condition:
            unsupported.append(reason)
    if operation != "unlink_regular":
        unsupported.append(f"operation_{operation}")
    if kind != "regular":
        unsupported.append(f"kind_{kind}")
    return (label, fsuid, parent_uid, target_uid, bits, sticky, content), sorted(unsupported)


def _parent_pass(write: bool, search: bool) -> bool:
    return write and search


def _owner_pass(parent_match: bool, target_match: bool) -> bool:
    return parent_match or target_match


def _decide(data: tuple) -> dict:
    label, fsuid, parent_uid, target_uid, bits, sticky, content = data
    write, search = bool(bits & 2), bool(bits & 1)
    parent_match, target_match = fsuid == parent_uid, fsuid == target_uid
    relation = "both" if parent_match and target_match else "parent" if parent_match else "target" if target_match else "neither"
    sticky_pass = not sticky or _owner_pass(parent_match, target_match)
    predicates = {"parent_write": write, "parent_search": search, "sticky_ownership": sticky_pass}
    return {"id": label, "model_permits_unlink": _parent_pass(write, search) and sticky_pass,
            "parent_access_bits": bits, "target_content_bits": content, "target_content_bits_consulted": False,
            "sticky_required": sticky, "ownership_relation": relation,
            "sticky_basis": relation if sticky else "not_required", "predicates": predicates,
            "denial_reasons": [name for name, passed in predicates.items() if not passed]}


def evaluate(request: object) -> dict:
    """Validate exact builtin declarations and evaluate predicates without effects.

    Common fields validate before root/version/context exclusions. A supported
    denial is complete; caller truth and real operation outcomes are unverified.
    """
    try:
        data, unsupported = _validated(request)
        if unsupported:
            return {**_outcome("unsupported", "outside_subset"), "unsupported_reasons": unsupported}
        return {**_outcome("model_complete", "normalized_unlink_predicates_only"), **_decide(data)}
    except _Invalid as error:
        return _outcome(error.status, error.reason)

def _depth(text: str) -> None:
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise _Invalid("depth_limit", "over_limit")
        elif char in "]}":
            depth -= 1


def _unique(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _Invalid("duplicate_key")
        result[key] = value
    return result


def _integer(token: str) -> int:
    if len(token) > MAX_NUMERIC_CHARS:
        raise _Invalid("numeric_token_limit", "over_limit")
    return int(token)


def _reject_number(token: str) -> None:
    if len(token) > MAX_NUMERIC_CHARS:
        raise _Invalid("numeric_token_limit", "over_limit")
    raise _Invalid("non_integer_number")


def analyze_json(raw: object) -> dict:
    """Strict UTF8 exact bytes, capped before JSON decoding, to bounded model report."""
    if type(raw) is not bytes:
        return _outcome("rejected", "input_type")
    if len(raw) > MAX_INPUT_BYTES:
        return _outcome("over_limit", "input_limit")
    try:
        text = raw.decode("utf-8", errors="strict")
        _depth(text)
        return evaluate(json.loads(text, object_pairs_hook=_unique, parse_int=_integer,
                                   parse_float=_reject_number, parse_constant=_reject_number))
    except _Invalid as error:
        return _outcome(error.status, error.reason)
    except (UnicodeError, ValueError, RecursionError):
        return _outcome("rejected", "invalid_json_or_utf8")


def serialize_report(report: dict) -> bytes:
    """Serialize trusted internally constructed reports; oversized fallback is incomplete.

    This is not an arbitrary-object public ingestion API. Accepted bounded reports
    cannot reach the cap; tests use labeled trusted oversized formatter seams.
    """
    def encode(value):
        return json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode("utf-8") + b"\n"
    encoded = encode(report)
    if len(encoded) > MAX_OUTPUT_BYTES:
        encoded = encode(_outcome("over_limit", "output_limit"))
        if len(encoded) > MAX_OUTPUT_BYTES:
            raise ValueError("trusted output budget smaller than fallback")
    return encoded
