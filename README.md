# Linux Sticky Directory Predicate Lab

A local learning tool that explains why file-content permissions and directory-entry
removal checks are different. It evaluates **invented declarations**, without reading
host identities, paths, modes or ACLs and without performing an unlink.

For the supported ordinary regular-entry subset:

```text
parent write AND parent search AND
(not sticky OR subject owns parent OR subject owns target)
```

The parent permissions are already selected, caller-declared bits: read=4, write=2,
search=1. Parent read and all target-content bits do not affect this conjunction.
Owning either entry does not repair a missing parent prerequisite. Both-owner is valid.

## Run

Requires Python 3.13; standard library only, no installation or API key.
From this directory, run:

```powershell
python -m sticky_lab demo
python -m sticky_lab --help
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python tools/check_mutations.py
```

The demo compares thirteen reports with independently frozen expected reports.
To send a fixture through bounded stdin, without entering a host path in the model:

```powershell
python -c "import json,sys; from sticky_lab.fixtures import oracles; sys.stdout.write(json.dumps(oracles()[0]['request']))" | python -m sticky_lab analyze
```

Exit codes: 0 model permits or demo passes; 1 model denies or demo fails; 2
unsupported/rejected/over-limit or invalid arguments; 3 checked I/O failure.
Help uses fixed ASCII usage. Invalid arguments emit a fixed JSON diagnostic,
without reflecting arguments. Reports are escaped compact UTF8 JSON plus LF;
text diagnostics use native newlines. Partial delivery is possible on I/O failure.

## Interface and architecture

`sticky_lab/core.py` contains exact-builtin admission, strict JSON parsing, the pure
predicate evaluator and a trusted-report serializer. `evaluate(object)` accepts
the fixed declaration schema; `analyze_json(bytes)` caps raw input before parsing.
`__main__.py` reads stdin or runs trusted fixtures and checks writes and flushes.
`fixtures.py` contains copies of the frozen data, with detached copies per call.
`fixtures/oracles.json` and its earlier hash receipt are the independent full-report
oracle. No user paths, import targets, commands or runtime adapters are accepted.

See [CONTRACT.md](CONTRACT.md) and [PLAN.md](PLAN.md) for exact keys, values,
validation/error order and output fields. Full common validation precedes every
root/context/operation exclusion and permission decision. Exact types use identity
checks before length, iteration, hash, equality or serialization; bool is not an
integer. Cycles and aliases cannot skip field validation. The caller must provide
stable input during a call; concurrent mutation is not supported.

Statuses: `model_complete` (including a complete denial), `unsupported`, `rejected`,
`over_limit`. Incomplete reports omit the predicate/grant decision. Every report
marks actual unlink, entry removal and storage reclamation **unverified**. Declared
input truth, permission-class selection, ancestor search and full policy are also
unverified. Limits: 16 KiB input; depth 6; numeric tokens 10 characters; identifiers
and enums 32 ASCII characters; 16 feature entries; 64 KiB output. Serializer accepts
trusted internal reports only. These logical limits are not a process sandbox or
a measured hard memory/time guarantee.

## Security model and limitations

Only positive nonzero filesystem subject IDs, identity mapping assumptions, declared
ordinary parent bits, regular entries and a single `unlink_regular` operation are
supported. Known root/capability/ACL/LSM/mount/idmap/namespace/readonly/immutable/
append-only/race/remote/descriptor/default-inheritance and richer context declarations
are unsupported. Unknown enum values are rejected. Rename/replacement needs source,
destination and additional policy checks and is deliberately outside this contract.

This is an advisory educational model. It must not be an authorization gate for a
real operation. It does not prove existence, effective identities, path traversal,
access selection, successful removal, storage reclamation or OS/filesystem safety.
See [SECURITY.md](SECURITY.md) for the threat model.

## Verification and learning

Verified on CPython 3.13.7 Windows: 27 tests in normal and optimized mode; thirteen
full frozen reports; an independent 512-case finite bit/equality domain per suite;
real normal/optimized child shutdown tests; three assertion-detected logic mutations
with zero errors and passing restored tests; compilation; installed Bandit on the
application and mutation helper. Exact results, receipt hashes and scanner scope
are recorded in [VERIFICATION.md](VERIFICATION.md) and `research/`.

The implementing agent performed an ECC self-review, not an independent audit.
Linux execution, upstream tests, hosted CI, CodeQL, dedicated secret scanning and
actual filesystem behavior remain unverified. No new Git repository, dependency
installation or publication was authorized. Prior labs remain separate.

An optional exercise: explain why a sticky target-owner with parent bits `2` still
gets a complete model denial, then change only parent bits to `3` and compare the
frozen reports. [LEARNING.md](LEARNING.md) records the source and CLI lessons.

## Sources, license and AI assistance

Original Python implementation and synthetic fixtures: MIT, copyright 2026 Jake
France. No upstream source code was copied or executed. Actual pinned Linux kernel
and Linux Test Project source, man-pages and PyFilesystem2 source were inspected
as research; their GPL/MIT licenses apply to their respective upstream code.
See [RESEARCH.md](RESEARCH.md) for exact sources/blobs, maintenance evidence,
alternative assessment and retrieval gaps. Previous owned ACL lab supplied reviewed
strict-JSON and CLI harness patterns; its original failure evidence is preserved.

Codex authored/reviewed/tested this project with Jake's authorization. One bounded
local qwen3.5:2b test-idea draft was rejected as an oracle; raw output is retained
separately. No remote worker, paid fallback or new spending was used.

## Publication status

See [publication review](PUBLICATION.md) for the October 5 source snapshot, fresh local checks, evidence boundaries and current hosted-check distinction.
