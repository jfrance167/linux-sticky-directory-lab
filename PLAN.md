# Sticky-directory predicate lab plan

Tier3 security learning project. Research selected coordinator04:12,October5,2026
under Jake's verified direct successor mandate. Existing chat sole writer; separate
linux-sticky-directory-lab. No code existed in the research-only phase.
Stages1–3 approved coordinator04:39; CONTRACT.md records the common/additional
conditions. Git initialization, installs and real operations remain excluded. New scope
cutoff October6 08:00 Eastern. RESEARCH.md records actual source/candidate/worker limits.

## Problem, recommendation and success

Teach the difference between file content access and removing a directory entry.
Recommend original stdlib model of one existing regular-file entry, using declared
parent access bits and sticky ownership predicates. Inputs are invented data;
outputs are conditional normalized predicates, never actual unlink permission,
entry removal, storage reclamation or filesystem transition.

Success: independently fixed checks/ownership explanations for parent write+search,
sticky parent-owner OR target-owner alternatives, target content-bit independence,
whole-common validation, explicit unsupported richer contexts and bounded pure API/
CLI with actual failed/help/diagnostic-process delivery checks. No runtime dependency
is necessary. Native kernel/LTP references and PyFilesystem comparison support
building rather than adoption/fork; no third-party code copied or executed.

Compare rename/replacement: two parents, source/destination existence/ownership,
same-inode shortcut, flags, cross-directory/type/mount/delegation checks substantially
increase scope. Defer it. Also defer parent DAC class/ACL evaluation; declared selected
access bits are an explicit input assumption, not recomputed from modes/identities.
Prior DAC/ACL labs teach that other stage independently. No imports from old labs.

## Proposed exact current schema

Root exact builtin dict keys id/version/profile/operation/subject/parent/target/context.
id/profile exact ASCII identifiers [A-Za-z][A-Za-z0-9_-]{0,31},≤32 chars. Supported
profile sticky_unlink_v1. version exact integer0..999999999;1 supported, bounded
other versions unsupported after all current common validation. Unknown valid
profiles likewise; no future-schema acceptance or partial evaluation.
operation exact enum unlink_regular/rename_regular/replace_regular: only first
supported, latter two known unsupported. Other values rejected.

subject exact {fsuid}: exact integer0..999999999; bool/subclasses invalid.
fsuid0 unsupported after all validation, not automatically granted. No actual process,
real/effective UID, group/name lookup. All UID comparisons assume ordinary identity
mapping of supplied filesystem IDs. Groups are deliberately absent because parent
access selection is a supplied operand; unknown extra fields rejected.

parent exact {owner_uid,declared_access_bits,sticky}. owner UID same range;
declared_access_bits exact integer0..7. It declares already-selected ordinary
permission predicates for this subject on this parent: bit2 write, bit1 search,
bit4 read. No automatic truth verification, class selection, ACL parsing or mode
interpretation. sticky exact builtin bool; integer0/1 is invalid. Sticky only belongs
to the parent, never inferred from target bits or a name.

target exact {owner_uid,kind,content_bits}. owner UID same range. kind exact enum
regular/directory/symlink/other/unknown: only regular supported, all other known
unsupported. content_bits exact integer0..7, required demonstrative metadata only;
never used to grant or deny the removal predicates. It is not a full mode, ACL,
inode flag, permissions derivation or proof of readability/writability.

context exact dict with:
- identity_mapping: assumed_identity/other/unknown; only assumed_identity supported.
- parent_permission_source: declared_ordinary_bits/acl/unknown; only first supported.
- ancestor_search: assumed_satisfied/not_satisfied/unknown; only first supported.
  Ancestor checking is excluded; not_satisfied is unsupported, not a simulated errno.
- privilege: ordinary_no_capabilities/capabilities/unknown; only first supported.
- entry_state: assumed_existing/missing/unknown; only first supported.
- excluded_features: exact list0..16 unique strings from acl,lsm,readonly,append_only,
  immutable,swapfile,mountpoint,idmap,namespace,symlink,race,remote_fs,descriptor,
  default_inheritance,unknown_context. Any present feature unsupported; unknown
  values/duplicates rejected. Bound exact strings before enum hashing.

These declarations are caller assumptions, not verified absence of kernel/filesystem
constraints. Missing entry/unknown kind/richer contexts intentionally remain incomplete;
do not simulate full errors. No actual paths, entry names, file handles or flags accepted.

## Validation and decision/report contract

Validation order: root shape, identifier/version/profile/operation, subject, parent,
target, context fixed field order then excluded list. Validate every common field
even behind root/unknown version/profile/operation/kind/context exclusions and even
when an early predicate obviously denies. Exact builtin dict/list/int/str/bool only;
inspect exact string key types before input-key hashing/equality. Reject custom hooks,
coercion/generators/cycles; this finite scalar tree rejects cycles at the first
incompatible field, with no recursive arbitrary-object traversal. Copy normalized
operands; never mutate callers. Caller concurrent mutation is outside API assumptions.

Valid supported decision is conjunction:
parent_write AND parent_search AND
(NOT parent_sticky OR fsuid==parent_owner_uid OR fsuid==target_owner_uid).
Ownership never repairs missing parent write/search. Nonsticky requires no ownership
match. Content read/write/execute bits never repair/deny any of these predicates.
Compute all three explanation predicates for a supported record, even after denial;
this is explanatory conjunction, not kernel instruction/errno precedence.

Every report: status/complete/reason, actual_unlink/entry_removed/storage_reclaimed
all "unverified", assumptions=[invented_filesystem_ids,identity_mapping_assumed,
declared_parent_access,declared_context_only], not_verified=[actual_unlink,
entry_removed,storage_reclaimed,input_truth,parent_access_selection,ancestor_search,
full_system_policy].

Complete status=model_complete, complete=true, reason=normalized_unlink_predicates_only,
including completed denials. Adds id, model_permits_unlink Boolean, parent_access_bits,
target_content_bits, target_content_bits_consulted=false, sticky_required Boolean,
ownership_relation=both/parent/target/neither, sticky_basis=not_required or that
relation, and predicates {parent_write:Boolean,parent_search:Boolean,sticky_ownership:
Boolean}. denial_reasons ordered parent_write,parent_search,sticky_ownership for
failed predicates; empty on permit. Do not emit actual errno, transition or actual
authorization claim. Ownership relations are explanatory equality only.

Unsupported: complete=false, reason=outside_subset, unsupported_reasons sorted
strings version/profile/fsuid_zero/operation_<value>/kind_<value>/<context_key>_<value>/
feature_<value>. No model_permits/checks/predicates/derived explanation. Rejected:
complete=false with fixed first reason object_shape/identifier/integer_range/enum/
boolean_type/list_shape/duplicate_feature/invalid_json_or_utf8/input_type/duplicate_key/
non_integer_number. Limits use over_limit complete=false reasons input_limit/
depth_limit/numeric_token_limit/list_limit/output_limit. Never reflect malformed values.

API semantic/cardinality/identifier bounds plus raw exact bytes≤16384 before strict
UTF8/JSON, lexical depth≤6 outside strings, numeric tokens≤10 incl sign, no floats/
nonfinite constants/duplicate keys. Integer endpoints same conservative range;
not a general uid_t/platform parser. Exact escaped compact UTF8 JSON+LF≤65536 output.
Single accepted reports cannot reach64KiB; labeled trusted oversized formatter/
reduced budget and patched CLI seams only, with nonrecursive fallback guard.

CLI analyze/demo: stdin cap+1, stdout binary checked exact count/flush, fixed checked
diagnostic on I/O failure and detach both dirty sinks before interpreter shutdown.
Checked help/parser write/flush as corrected ACL precedent; public JSON input values
never appear as raw terminal prose. Exit0 permits/pass demo,1 denies/fail demo,
2 incomplete,3 I/O delivery failure. Partial stdout/failed diagnostic delivery remain
possible, no atomic guarantee. Help/usage handling bounded to trusted CLI arguments;
freeze argument-error output separately before implementation. No user file path.

## Independent proposed cases

Baseline fsuid202,parentUID101,targetUID303,regular/ordinary context. Table values
are manually derived from inspected kernel predicates, not candidate-generated.
W/S/T columns are full independent expected predicate booleans. Target content
bits are a deliberate demonstrative operand, no filesystem access result.

| Case | fsuid/parentUID/targetUID | Parent bits/sticky | Content | W/S/T | Basis | Model |
|---|---|---|---|---|---|---|
| Ordinary no content bits |202/101/303|3/false|0|true/true/true|not_required|permit|
| Content bits all present |202/101/303|3/false|7|true/true/true|not_required|permit|
| Sticky unrelated subject |202/101/303|3/true|7|true/true/false|neither|deny|
| Sticky parent owner |101/101/303|3/true|0|true/true/true|parent|permit|
| Sticky target owner |303/101/303|3/true|0|true/true/true|target|permit|
| Both owner equalities |303/303/303|3/true|0|true/true/true|both|permit|
| Parent owner missing write |101/101/303|1/true|7|false/true/true|parent|deny|
| Target owner missing search |303/101/303|2/true|7|true/false/true|target|deny|
| Parent read alone insufficient |202/101/303|4/false|7|false/false/true|not_required|deny|
| Parent no bits/content all |202/101/303|0/false|7|false/false/true|not_required|deny|
| All parent bits still sticky |202/101/303|7/true|7|true/true/false|neither|deny|
| Owner with full parent bits |101/101/303|7/true|0|true/true/true|parent|permit|
| Parent read/search missing write |202/101/303|5/false|7|false/true/true|not_required|deny|

Paired repairs: sticky unrelated → parent/target equality or sticky=false; missing
parent write/search → parent bits3. Changing only content0..7 does not repair a
denial. Root, rename, nonregular, unknown/missing/context examples unsupported after
common validation; malformed target content bool behind root/unknown gates rejected.
Before core code after approval expand all thirteen full reports independently,
freeze schema/status/error/help details and hashes; no production oracle generation.

Property proposal:8 parent bits ×2 sticky ×4 independent owner-match combinations
×8 content values=512 exact bit-position-set/equality comparisons, all non-root IDs.
Read-bit invariance and content invariance explicit; both owner matches possible
without unioning unrelated permissions. Counts are finite synthetic domains, not
Linux system coverage. Freeze domain/oracles before implementation.

## Threat model, risks and staged acceptance

Assets: correct conditional predicate explanation, bounded admission, honest status,
no host effects. Adversarial inputs can be ambiguous, coercive, oversized, cyclic,
falsely declare permissions/context, or treat model permit as actual deletion.
Mitigate with exact finite schema, all-field validation, bounded parse/report,
no paths/ambient capabilities, explicit input assumptions and unverified outcomes.
No mitigation authenticates supplied bits or replaces platform authorization.

1. Freeze and implement pure normalized predicates. Done: all thirteen full reports
   frozen before core, exact types/common/exclusion ordering, owner OR alternatives,
   write+search conjunction, content independence, no host functionality. Verify
   independent cases/admission/immutability/finite512 property domain and source review.
2. Bounded CLI and regression tests. Depends1. Done: ordinary/deny/incomplete exits,
   strict raw/depth/token/builtin/cycle/duplicate/enum/bounds, labeled unreachable
   output seams, help/diagnostic/short/flush paths. Actual Python normal/-O native
   closed pipes and labeled dirty-stream child seams required, not mocked returns
   as shutdown evidence. Source/capability checks prohibit unlink/remove/rename/
   filesystem/identity/permission/network/process calls in core; harness preimported.
3. Review and documentation. Depends1–2. Done: targeted OR-prerequisites/AND-ownership/
   target-content-gate mutants produce assertion failures, no errors, restored pass;
   normal/-O tests, compile/installed SAST; actual ECC source/caller/test self-review,
   corrections/rechecks, source/exit receipts and README/SECURITY/MIT/AI assistance/
   DECISIONS/LEARNING/STATE/vault milestone. Prepared minimal pinned CI only if
   separately authorized; Git initialization/remote/publication currently excluded.

Ordered fine-grained task checklist is tasks/todo.md; tasks/plan.md links this single
authoritative plan. Contract/full oracles predate application code; current stage
completion is in STATE/VERIFICATION. Definitions of done require observed evidence.

Limitations retained: Windows-only verified execution; no Linux/native/upstream
test or full POSIX/kernel/full-system conformance, no actual entry/permission/identity/
ACL/path operation, no root/privileges/LSM/mount/idmap/namespace/remote/replacement
semantics, hard memory/time isolation, hosted CI/CodeQL/advisory/hash-lock/dedicated
secret-scan assurance. No real/private data, installs/VM/container change, new chat/
subagent/scheduler/reply loop/publication/spending or parent/shared/prior-project edits.

Local Ollama bounded draft failed acceptance; raw kept and reviewed corrections
separate. Free remote considered but no fresh verified route within shared-write
exclusions; no remote/paid fallback. Codex source/security judgments, implementation,
review and checks. Approved stages locally complete; see VERIFICATION.
