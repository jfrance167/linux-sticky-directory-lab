# Security model

Assets: truthful bounded model reports, input preservation, local host integrity,
and the distinction between a declared predicate result and actual authorization.

Trust boundaries: stdin/exact-builtin declarations are untrusted data; fixed schema,
source-backed formula and manually frozen fixtures are trusted application material.
Reports are advisory output. The serializer is an internal trusted-object utility,
not an ingestion boundary. The test harness launches only this owned Python code
with invented data; it is not an execution sandbox for unfamiliar code.

Threats and controls:

- Misleading or malformed declarations: exact shapes/types, common admission before
  exclusions or decisions; strict non-duplicate/non-floating JSON; explicit incomplete
  states and unverified truth/context. Valid invented lies remain possible.
- Hook-bearing Python subclasses/metaclasses/keys: type identity before native hooks;
  exact string key type/length before set membership. Benign raising probes verify
  rejection without hook calls. Arbitrary accepted-code execution is absent.
- Resource-driven input/output: byte/depth/token/list/string/output bounds. Caller
  allocations and Python runtime overhead are outside these logical limits; no hard
  RSS/time isolation claim. Accepted reports cannot reach the defensive output cap.
- Permission confusion: parent write/search conjunction; sticky parent/target-owner
  disjunction; target content/read-bit invariance. Independent frozen reports and
  finite-domain controls plus three targeted mutation/restoration checks.
- Dirty/short/closed output: checked writes/flushes for reports/help/errors; both
  public sinks detached on failure before CPython shutdown; exit3 verified in real
  children. Partial delivered bytes cannot be rolled back; no atomicity claim.
- Terminal/argument reflection: escaped JSON, bounded ASCII identifiers and fixed
  parser diagnostics. Help is fixed text; no user argv reflection.

Known unsupported features include root/privilege exceptions, ACL selection, LSM,
readonly/append-only/immutable/swap/mountpoint/idmap/namespace, path/symlink races,
remote filesystems, descriptors and creation/default-inheritance. Rename, replacement,
directory/symlink removal and live Linux operations need different contracts.

No real identities, filesystem paths, deletion, rename, mode/owner/ACL mutation,
network use or third-party target testing occurs in application code. Use only
invented public fixtures. Do not use a model grant to authorize a real unlink.

No external disclosure/reporting integration is configured; security concerns can
be reviewed locally with Jake. Publication, merge and deployment require separate
human authorization. This release is local learning work, not certified containment.
