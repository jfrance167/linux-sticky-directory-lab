# Sticky-directory removal research — October 5, 2026

Historical research selected coordinator04:12 under Jake's verified direct successor
mandate; no application code existed in that phase. Stages1–3 subsequently approved
04:39. Current completion is in STATE/VERIFICATION; source observations below remain
research evidence, including retrieval gaps. No Git/install/host operations.

## Reuse and distinct gap

Read selected-vault Home/Codex Integration, Linux File Modes and Directory Access,
Linux Permission Model research plan, Creation Mask project note and ACL project
plus its authoritative CLI correction. Prior DAC/creation/ACL contracts explicitly
exclude sticky/removal. Bounded local filename/content and relevant vault searches
found those references, not a matching standalone lab; this is not exhaustive.
Reuse reviewed strict JSON/exact-type/status/documentation and corrected checked
CLI delivery patterns only after approval; do not import old ACL/DAC implementation
as though it computes this operation. No prior suite rerun or parent/shared edits.

## Primary semantic evidence

[unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html) distinguishes removal
of a name from eventual storage reclamation. Its errors cover containing-directory
write, pathname search, sticky ownership/privilege, flags and read-only state.
No claim that a modeled permit removes a name or reclaims storage.
[inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html) describes sticky
directories; [rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html) shows
source/destination replacement conditions and additional semantics. Man-page effective
UID wording is not used to infer identities: actual kernel predicates below use fsuid
with mount mapping. All browser sources primary; no third-party tutorial as oracle.

Connected GitHub inspected actual files at Linux commit
a90ee4305c4a5df72c11b31dacfdc76e00fcf78a:
- fs/namei.c blob20a6534ea3efffd6686e3b49c3e76f399c966f9e: __check_sticky,
  may_delete_dentry, vfs_unlink/filename_unlinkat and vfs_rename relevant bodies.
- include/linux/fs.h blobf9d1e05e8ae68ea61561acb4a9ed556150708bb6: check_sticky
  immediately passes when parent lacks S_ISVTX; otherwise delegates ownership check.
- COPYING bloba635a38ef9405fdfcfe97f3a435393c1e9cae971: kernel GPL2 with syscall
  note; namei source has GPL2 SPDX. Source comparison only, no code copied/executed.

[Pinned namei source](https://github.com/torvalds/linux/blob/a90ee4305c4a5df72c11b31dacfdc76e00fcf78a/fs/namei.c)
uses current_fsuid, mapped target UID equality or mapped parent UID equality, else
CAP_FOWNER. may_delete_dentry separately requires parent MAY_WRITE|MAY_EXEC and
checks append/immutable/swap/unmapped IDs/types/dead/NFS conditions. vfs_unlink adds
filesystem operation support, mountpoint, LSM, delegation and filesystem action.
The proposed model uses only declared parent access bits and nonprivileged sticky
ownership, assuming identity mapping and richer context. Target content permission
bits are not consulted by these selected predicates. This is a narrow conditional
predicate model, not a syscall validator or full may_delete_dentry emulation.

vfs_rename checks old-entry deletion, then new-entry creation or replacement deletion;
same-inode shortcut, flags/type/mount/cross-directory/LSM/locking/delegation make
rename much wider. Recommend deferring rename/replacement instead of treating it
as one unlink predicate or claiming a filesystem transition.

## Candidate 1: LTP, native correctness references

[LTP](https://github.com/linux-test-project/ltp) commit
dca9f0d272b2923256852fc37abd222b533d91e0 (returned latest commit October1,2026,
compiler-warning correction). Actual connected source, full five-file unlink
directory inventory and relevant bodies inspected:

| Path under testcases/kernel/syscalls | Blob | Relevant observed assertions |
|---|---|---|
| unlink/unlink05.c | 8de2d8bc2573ff1021d9d954e15b62901e71b82c | regular/FIFO success then existence check |
| unlink/unlink07.c | b4b70d2704ac916063005e0c32fb0c6580499955 | missing/empty/invalid path conditions |
| unlink/unlink08.c | c1fa8f31d02e907026a2f4fd315f13acb10fbbb2 | parent write/search EACCES, directory EISDIR |
| unlink/unlink09.c | 10d4e8a448c69145224b28bdaa414c16c4165b23 | immutable/append-only EPERM |
| unlink/unlink10.c | 2d6ec8ce1428dde8e589477a4c8205c4ac8cdc84 | read-only EROFS |
| rename/rename12.c | 3e717f24947a46a4ee2f77eebacdd2f87d161669 | nonprivileged sticky-source rename EPERM/EACCES |

The inspected unlink directory does not provide a direct positive/negative sticky
regular-file unlink matrix; rename12 is an adjacent native test, not proof of that
matrix. Source-derived synthetic cases will therefore have explicit live/upstream
coverage limits. These tests create files, change modes/identities, use ioctl/root/
mounts/forks and real unlink/rename: do not run/install them here.

Sources are GPL2-or-later SPDX; COPYING d159169d1050894d3ea3b98e1c965c4058208fe1
GPL2 preamble inspected. Reusing code requires license/notice/source obligations,
unnecessary for original predicates. unlink/Makefile044619fb8724a13fac9d6d2b859b5a63c6fc9554
uses shared C harness build includes. Native C/libc/LTP harness plus kernel/root/
filesystem-specific test prerequisites cannot become a Windows stdlib model dependency.

Actual ci-docker-build.yml b117547d8ad8755ff01e73bf253c4a2444f709a3 includes compiler/
autotools/build/C/shell/metadata checks across distros, minimum contents:read, but
checkout@v1, mutable distro tags, package installs and privileged containers. Do not
copy or execute that configuration. Current open PR1341 alleges cleanup exit errors;
issue1336 proposes test naming. Neither was validated as a security finding. No
upstream tests/CI, full advisory/Scorecard audit or dependency safety certification.
README.md returned404; root inventory discovered README.rst/INSTALL/configure.ac,
but subsequent connector retrieval and raw web fallback failed. Full install docs
were not obtained; dependency conclusions above are limited to actual source/CI.

## Candidate 2: PyFilesystem2, Python abstraction comparison

[PyFilesystem2](https://github.com/PyFilesystem/pyfilesystem2), default master latest
returned77a8562785fc37cb2e30bdcd39c133097ba62dce May17,2025 docs-link change; prior
returned commit October18,2022 contributors change. Repo unarchived, pushed May17,2025;
these observations and open issue598's abandonment allegation do not prove status
or safety. PR600/601 describe filesize rounding/type handling, not sticky enforcement;
not executed/validated as security findings.

Actual source/docs/test/config/license files inspected:
Initial memoryfs/setup/config/license/direct-test requests used default master and
are bound by returned blob IDs; README/permissions/shared-tests/CI explicitly used
77a8562785fc37cb2e30bdcd39c133097ba62dce. No universal snapshot attestation implied.
- README0f1326b121c30c2a925528a662de33f7cec2c8d3: filesystem abstraction across
  local/archive/network backends, not a supplied authorization evaluator.
- fs/memoryfs.py0ca5ce16aaeb8a0f09e9fefefd939d99817656fc remove validates path,
  existence/file type, locks and removes an entry; no supplied fsuid/sticky predicate.
- fs/permissions.py3fee3352e226fc932eff9d1ce73b75e022b2e299 represents permission
  names/bits including sticky, not operation authorization.
- tests/test_memoryfs.py6537fac27d48e0af1e6c17ea30aa78e3313104c1 inherits shared
  FSTestCases; fs/test.py32e6ea5c311a8b5a76487904bcae53a023128096 test_remove checks
  entry removal/missing/file-type exceptions, not Linux sticky ownership.
- setup.pyc4e2465a37719370d7f7bce91c180c0c1645276f loads project version at build;
  setup.cfg57c6f40b5258b7c30f13b9880dcfb67c4b8281e0 uses setuptools, appdirs~1.4.3,
  six~1.10 and legacy conditional packages; Python/typing/typecheck/test matrix older
  than this tested3.13 environment. No installation/build/version execution.
- LICENSE34845692b8b5ffeb8ec684f1abdd775e7a6bd179 MIT requires preserving notices
  if copied. No third-party code copied, so no dependency/attribution import needed.
- test.yml4be9098a62df9820d6a5366d17e415fb076456d3: tox/coverage/linters, old Python
  matrix, mutable checkout/setup/artifact actions, develop Coveralls action, pip
  upgrades/unpinned tool installs. Not adopted; no hosted success claim.

MemoryFS is useful for abstraction tests but does not supply the required semantics;
forking would add broad backend/dependency surface without replacing this predicate
work. Older packaging/mutable CI are review limitations, not confirmed vulnerabilities.

## Recommendation, workers and limits

**Build** an original stdlib declared-parent-bits + sticky ownership model after
approval. No suitable adoption/fork was found in the performed bounded searches;
unrelated name/description results are not evidence of useful implementation.
Connected repository search initially failed transport, subsequent source/search
calls succeeded, final README/INSTALL/commit calls failed again. Kernel source
revision/blob is known; its commit metadata date was not retrieved.

One existing loopback Ollama qwen3.5:2b220-token/30s ideas request completed:
5.762s172tokens, stop/exit0; raw draft retained separately. Three suggestions require
ownership without sticky, propose an out-of-scope CSV input format, or deny
because target content bits are present. Rejected as oracle. One sticky ownership
reminder repeats the brief, independently kernel-corroborated. No automatic execution,
retry or worker code. Codex handles source/security judgments and reviewed planning.
Remote free OpenRouter considered via routing guide; current07:34 startup snapshot
is stale for this draft, and refreshing shared tooling is excluded. No verified
eligible fresh route; no remote inference/new spending/paid fallback. Laya's existing
categorization/refund triage schema is unrelated to this semantic task.

Firecrawl CLI installed, but zero-price quota eligibility unverified: no chargeable
call. Included primary-source web/connected GitHub used instead. Final web raw-file
fallback failed connection; no retry loop/credentials/unsafe alternate download.
No exhaustive repository/issue/license/security audit, upstream execution, Linux
runtime comparison, actual filesystem/identity/context truth or universal unlink
permission/conformance claim. Planned MIT original code, credited primary sources
and AI assistance; no project code until concrete coordinator approval.
