"""Independent frozen full reports, finite bit-set/equality domain and no hooks."""

from copy import deepcopy
from contextlib import ExitStack
import builtins
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import unittest
from unittest.mock import patch

from sticky_lab import core
from sticky_lab.fixtures import oracles


def request(**overrides):
    value = oracles()[0]["request"]
    value["id"] = "Invented"
    for field, replacement in overrides.items():
        value[field] = replacement
    return value


class CoreTests(unittest.TestCase):
    def incomplete(self, value, status="rejected", reason=None):
        report = core.evaluate(value)
        self.assertEqual(report["status"], status)
        self.assertFalse(report["complete"])
        if reason:
            self.assertEqual(report["reason"], reason)
        for field in ("model_permits_unlink", "predicates", "ownership_relation", "denial_reasons"):
            self.assertNotIn(field, report)
        return report

    def test_frozen_full_oracles(self):
        root = Path(__file__).resolve().parents[1]
        raw = (root / "fixtures/oracles.json").read_bytes()
        receipt = json.loads((root / "research/oracle-freeze.json").read_bytes())
        self.assertEqual(receipt["application_files"], [])
        self.assertEqual(receipt["property_domain"]["total"], 512)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt["oracle_sha256"])
        fixtures = json.loads(raw)
        self.assertEqual(fixtures, oracles())
        self.assertEqual(len(fixtures), 13)
        for fixture in fixtures:
            with self.subTest(id=fixture["request"]["id"]):
                self.assertEqual(core.evaluate(fixture["request"]), fixture["expected"])
                self.assertEqual(core.analyze_json(json.dumps(fixture["request"]).encode()), fixture["expected"])

    def test_prerequisite_regression(self):
        value = oracles()[6]["request"]
        self.assertFalse(core.evaluate(value)["model_permits_unlink"])
        value["parent"]["declared_access_bits"] = 3
        self.assertTrue(core.evaluate(value)["model_permits_unlink"])

    def test_ownership_regression(self):
        value = oracles()[3]["request"]
        self.assertTrue(core.evaluate(value)["model_permits_unlink"])
        value["subject"]["fsuid"] = 202
        self.assertFalse(core.evaluate(value)["model_permits_unlink"])

    def test_content_regression(self):
        self.assertTrue(core.evaluate(request())["model_permits_unlink"])

    def test_independent_domain_512(self):
        count = 0
        for bits in range(8):
            positions = {i for i in range(3) if (bits // (2 ** i)) % 2}
            for sticky in (False, True):
                for parent_match in (False, True):
                    for target_match in (False, True):
                        for content in range(8):
                            value = request()
                            value["parent"].update(owner_uid=202 if parent_match else 101,
                                                   sticky=sticky, declared_access_bits=bits)
                            value["target"].update(owner_uid=202 if target_match else 303, content_bits=content)
                            expected = ({0, 1} <= positions) and (not sticky or parent_match or target_match)
                            result = core.evaluate(value)
                            self.assertEqual(result["model_permits_unlink"], expected)
                            self.assertFalse(result["target_content_bits_consulted"])
                            count += 1
        self.assertEqual(count, 512)

    def test_read_content_invariance_and_immutability(self):
        value = request()
        before = deepcopy(value)
        baseline = core.evaluate(value)
        self.assertEqual(value, before)
        for bits in (3, 7):
            for content in range(8):
                value["parent"]["declared_access_bits"] = bits
                value["target"]["content_bits"] = content
                result = core.evaluate(value)
                self.assertEqual(result["predicates"], baseline["predicates"])
                self.assertEqual(result["model_permits_unlink"], baseline["model_permits_unlink"])
        baseline["assumptions"].clear()
        self.assertTrue(core.evaluate(value)["assumptions"])

    def test_common_validation_before_all_exclusions(self):
        for field in ("root", "version", "profile", "operation", "kind", "context"):
            value = request()
            if field == "root":
                value["subject"]["fsuid"] = 0
            elif field in ("version", "profile", "operation"):
                value[field] = {"version": 2, "profile": "Future", "operation": "rename_regular"}[field]
            elif field == "kind":
                value["target"]["kind"] = "directory"
            else:
                value["context"]["privilege"] = "unknown"
            value["target"]["content_bits"] = True
            self.incomplete(value, reason="integer_range")
        value = request()
        value["parent"]["declared_access_bits"] = 0
        value["context"]["excluded_features"] = ["invalid"]
        self.incomplete(value, reason="enum")

    def test_unsupported_all_known_contexts_sorted(self):
        value = request(version=2, profile="Future", operation="replace_regular")
        value["subject"]["fsuid"] = 0
        value["target"]["kind"] = "symlink"
        value["context"]["excluded_features"] = ["lsm", "acl"]
        expected = ["feature_acl", "feature_lsm", "fsuid_zero", "kind_symlink", "operation_replace_regular", "profile", "version"]
        self.assertEqual(self.incomplete(value, "unsupported")["unsupported_reasons"], expected)
        for field, choices in core.CONTEXT.items():
            for choice in choices[1:]:
                value = request()
                value["context"][field] = choice
                self.incomplete(value, "unsupported")
        for kind in ("directory", "symlink", "other", "unknown"):
            value = request()
            value["target"]["kind"] = kind
            self.incomplete(value, "unsupported")
        for feature in core.FEATURES:
            value = request()
            value["context"]["excluded_features"] = [feature]
            self.incomplete(value, "unsupported")

    def test_identity_admission_no_metaclass_or_subclass_hooks(self):
        calls = []
        class Meta(type):
            def __eq__(cls, other):
                calls.append("metaclass_equality")
                raise AssertionError("metaclass equality called")
            def __hash__(cls):
                calls.append("metaclass_hash")
                raise AssertionError("metaclass hash called")
        class Mapping(dict, metaclass=Meta):
            def __iter__(self):
                calls.append("iteration")
                raise AssertionError("custom iteration called")
            def __len__(self):
                calls.append("length")
                raise AssertionError("custom length called")
        class Number(int, metaclass=Meta):
            def __le__(self, other):
                calls.append("comparison")
                raise AssertionError("custom comparison called")
        class Text(str, metaclass=Meta):
            def __eq__(self, other):
                calls.append("string_equality")
                raise AssertionError("custom equality called")
        class Sequence(list, metaclass=Meta):
            def __iter__(self):
                calls.append("iteration")
                raise AssertionError("custom iteration called")
        self.incomplete(Mapping(request()))
        self.incomplete(request(version=Number(1)))
        self.incomplete(request(profile=Text("sticky_unlink_v1")))
        value = request()
        value["context"]["privilege"] = Text("ordinary_no_capabilities")
        self.incomplete(value)
        value = request()
        value["context"]["excluded_features"] = Sequence([])
        self.incomplete(value)
        self.assertEqual(calls, [])

    def test_custom_keys_aliases_and_cycles(self):
        active = False
        class Key(str):
            def __hash__(self):
                if active:
                    raise AssertionError("key hashing invoked")
                return str.__hash__(self)
            def __eq__(self, other):
                if active:
                    raise AssertionError("key equality invoked")
                return str.__eq__(self, other)
        value = request()
        value[Key("wrong")] = value.pop("id")
        active = True
        self.incomplete(value, reason="object_shape")
        value = request()
        value["x"*10000] = value.pop("id")
        self.incomplete(value, reason="object_shape")
        value = request()
        value["target"] = value["parent"]
        self.incomplete(value)
        value = request()
        value["target"] = value
        self.incomplete(value)
        value = request()
        value["context"]["excluded_features"].append(value["context"]["excluded_features"])
        self.incomplete(value)
        value = request()
        shared = "unknown"
        for field in core.CONTEXT:
            value["context"][field] = shared
        result = self.incomplete(value, "unsupported")
        self.assertEqual(len(result["unsupported_reasons"]), 5)

    def test_scalar_boundaries_and_shapes(self):
        for bad in (True, -1, 1_000_000_000, 1.0, "1", None):
            self.incomplete(request(version=bad))
            value = request()
            value["subject"]["fsuid"] = bad
            self.incomplete(value)
        value = request()
        value["subject"]["fsuid"] = 999_999_999
        self.assertTrue(core.evaluate(value)["complete"])
        for bad in (True, -1, 8, "3"):
            value = request()
            value["parent"]["declared_access_bits"] = bad
            self.incomplete(value)
            value = request()
            value["target"]["content_bits"] = bad
            self.incomplete(value)
        for bad in (0, 1, None, "true"):
            value = request()
            value["parent"]["sticky"] = bad
            self.incomplete(value, reason="boolean_type")
        for bad in ("x"*33, "\ud800", "Bad\n", "é", ""):
            self.incomplete(request(id=bad), reason="identifier")
        for field in ("operation", "profile"):
            value = request()
            del value[field]
            self.incomplete(value)

    def test_features_and_enum_bounds(self):
        for bad in (["invalid"], ["x"*10000], [object()], ["lsm", "lsm"], ("lsm",)):
            value = request()
            value["context"]["excluded_features"] = bad
            self.incomplete(value)
        value = request()
        value["context"]["excluded_features"] = list(core.FEATURES)
        self.incomplete(value, "unsupported")
        value["context"]["excluded_features"] = ["lsm"]*17
        self.incomplete(value, "over_limit", "list_limit")
        for field in core.CONTEXT:
            value = request()
            value["context"][field] = "bad"
            self.incomplete(value, reason="enum")

    def test_strict_raw_parser_boundaries(self):
        raw = json.dumps(request()).encode()
        exact = raw+b" "*(core.MAX_INPUT_BYTES-len(raw))
        self.assertTrue(core.analyze_json(exact)["complete"])
        self.assertEqual(core.analyze_json(exact+b" ")["reason"], "input_limit")
        for raw, reason in ((b"["*7+b"0"+b"]"*7,"depth_limit"),
                            (b'{"x":10000000000}',"numeric_token_limit"),
                            (b'{"x":1.5}',"non_integer_number"), (b'{"x":NaN}',"non_integer_number"),
                            (b'{"x":1,"x":2}',"duplicate_key"), (b'\xff',"invalid_json_or_utf8")):
            self.assertEqual(core.analyze_json(raw)["reason"], reason)
        for bad in ("{}", bytearray(b"{}"), memoryview(b"{}")):
            self.assertEqual(core.analyze_json(bad)["reason"], "input_type")
        # Parser-only wrong-schema seams, not admitted records.
        self.assertEqual(core.analyze_json(b"["*6+b"0"+b"]"*6)["reason"], "object_shape")
        self.assertEqual(core.analyze_json(b'{"x":-999999999}')["reason"], "object_shape")
        self.assertEqual(core.analyze_json(b'{"x":"[[[[[[["}')["reason"], "object_shape")

    def test_trusted_formatter_seams(self):
        length = len(core.serialize_report({"x":""}))
        exact = core.serialize_report({"x":"a"*(core.MAX_OUTPUT_BYTES-length)})
        self.assertEqual(len(exact), core.MAX_OUTPUT_BYTES)
        result = json.loads(core.serialize_report({"x":"a"*(core.MAX_OUTPUT_BYTES-length+1)}))
        self.assertEqual((result["status"],result["complete"],result["reason"]),("over_limit",False,"output_limit"))
        self.assertNotIn("predicates", result)
        self.assertIn(b"\\u001b",core.serialize_report({"trusted":"\x1b"}))
        with patch.object(core,"MAX_OUTPUT_BYTES",1):
            with self.assertRaises(ValueError):
                core.serialize_report({"x":"y"})

    def test_core_has_no_host_capabilities(self):
        value = request()
        with ExitStack() as guards:
            for module,name in ((builtins,"open"),(builtins,"eval"),(builtins,"exec"),
                                (os,"remove"),(os,"unlink"),(os,"rename"),(os,"stat"),(os,"chmod"),
                                (os,"system"),(subprocess,"Popen"),(socket,"socket")):
                guards.enter_context(patch.object(module,name,side_effect=AssertionError("forbidden capability")))
            for name in ("getuid","geteuid","getgid","getgroups","chown","getxattr","setxattr"):
                if hasattr(os,name):
                    guards.enter_context(patch.object(os,name,side_effect=AssertionError("forbidden identity/ACL")))
            self.assertTrue(core.evaluate(value)["model_permits_unlink"])
            self.assertTrue(core.analyze_json(json.dumps(value).encode())["complete"])
            self.assertTrue(core.serialize_report(core.evaluate(value)).endswith(b"\n"))
