# Verified local results — October 5, 2026

CPython3.13.7 Windows AMD64; final capture09:05:07 UTC. Standard-library application;
existing Bandit1.9.4. All eight recorded checks exit0 in research/check-status.json.

| Check | Observed |
| --- | --- |
| Normal suite | 27 tests,0failures/errors |
| Optimized suite | 27 tests,0failures/errors |
| Independent oracles | 13 full API/JSON/demo reports match |
| Independent finite domain | 512 bit-position/equality cases per suite |
| Interpreter delivery | 46 child observations per suite, normal and optimized children |
| Mutations, normal/-O | Three faults each1assertion/0errors; three restored passes |
| Demos, normal/-O | 13/13 pass |
| Compile | Application/tests/tools pass |
| Bandit | Application/tools282 non-comment LoC,0findings/errors/skips/suppressions |
| ECC | Actual implementing-agent self-review; no unresolved actionable findings |

Reproduce from this directory:

```text
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python tools/check_mutations.py
python -O tools/check_mutations.py
python -m sticky_lab demo
python -O -m sticky_lab demo
python -m compileall -q sticky_lab tests tools
python -m bandit -r sticky_lab tools -f json
```

research/normal-suite.stdout.json and optimized-suite.stdout.json contain full logs,
actual return codes/stdout/stderr and every child's arguments/mode/stream setup.
Each suite includes22 native pipe/healthy controls and24 labeled stream seams:
12dirty short/flush,12closed-Python/absent-stream. Both run normal and optimized
children. Healthy controls cover permit/deny/full demo/help and fixed parser JSON;
native help/report/parser failures include both failed sinks. Explicit stdin barriers
close readers before output. Ten-second child timeout is a harness bound only.

Mutations change prerequisite AND→OR, ownership OR→AND and add incorrect target
content write gating, in memory without source edits. Saved normal/-O receipts include
assertion tracebacks and restored outcomes. Errors never count as detection; no
mutation-coverage score. Frozen-before-code13 full-report oracle SHA256 remains
a3ca0f81377d652662c71fc61a692f052e43420c41620b1335c89d65f47f6f3b;
research/oracle-freeze.json records zero application files at that milestone.

Admission tests include benign raising metaclass equality/hash, mapping length/
iteration, scalar subclasses and custom keys, with zero hook calls on rejection.
Malformed trailing fields behind exclusions, cycles/aliases/repeated leaves/input
preservation, list/string/raw/depth/token bounds and trusted output seams covered.
Accepted reports cannot reach the output cap; formatter oversize/tiny-budget and
wrong-schema parser-depth seams are labeled, not admitted record claims.

Core source imports only json/re. Preimported harness guards filesystem/identity/
network/process functions during pure API checks; actual source paths reviewed.
Bandit scans sticky_lab and tools/check_mutations.py, not tests. Trusted Python child
launches and fixture reads were manually reviewed. Source/content review found no
credentials/private target data; no dedicated secret scan or history scan performed.
No new repository/history, installs, native Linux/upstream tests, hosted CI, CodeQL,
advisory certification or hard resource measurements. Source/runtime truth and
actual unlink/entry removal/storage reclamation remain unverified.

ECC verification-loop phase dispositions: build/compile PASS; tests PASS; security
Bandit/self-review PASS within listed scope; source inventory review PASS (new files,
no Git baseline). Types/lint NOT RUN (no configured tooling, no install); hosted CI,
Linux/upstream tests, dedicated secret scanner and independent audit NOT RUN; Git
diff/history NOT APPLICABLE (new repository forbidden). Bounded credential-pattern
search found no matching files; absence is not a secret-scanning safety verdict.

research/source-receipt.json binds current source/tests/tools/oracles/raw results;
integrity evidence, not a signature or safety guarantee. Research checkpoint is
historical documentation-only evidence, not the final source inventory.
