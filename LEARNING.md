# Learning

Content permissions and directory-entry removal predicates answer different
questions. In this modeled ordinary subset, parent write/search are both required;
sticky adds owner alternatives. Owning the target does not supply a missing parent
predicate. A writable target does not satisfy an unrelated sticky owner check.

Kernel identities are filesystem IDs with mapping, not a portable inference from
man-page effective-UID wording or a username. Supplied IDs/access bits/context are
assumptions, no proof of a real operation. Name removal also does not establish
storage reclamation: link/descriptor lifetime is outside the model.

Rename/replacement checks source and destination with additional cases; treating
it as this same three-predicate conjunction would omit relevant conditions.
Native tests illustrate real effects/prerequisites but were only inspected, not run.
The local draft confused nonsticky ownership and target content gates; retain those
mistakes as reviewed evidence, never expected test truth.

27 tests normal/-O include13 frozen reports and512 finite-domain cases; finite
synthetic coverage is not Linux system coverage. Three mutants caused assertion
failures,0errors; restored checks pass. Type identity must precede native operations,
even comparing class objects, because metaclasses can override equality/hash.
Native key length must be checked before set comparison. No-hook probes establish
bounded rejection behavior, not permission to execute hostile Python objects.

CPython shutdown can replace a handled pipe failure with exit120 if a dirty sink
flushes again. Detaching both public sinks avoids that retry; real normal/-O children
verify help/report/parser/diagnostic behavior. Native pipe errors, closed Python
ValueError and absent/short/flush seams are separate evidence; no atomicity claim.
