# Installer improvement review — 16 November 2026

Scope: installer, diagnostic, optional SEO setup, probe runner, tests and CI.
Ranked by impact, demonstrated gaps and fit with the project-only, dependency-free
contract. The first ten are the implementation batch (including existing PR #2).
The remaining fifteen are proposals, not commitments or verified defects.

## Sources and reuse

- [Agent Skills specification](https://agentskills.io/specification): metadata
  bounds and portable catalog structure; basis for 1, 9, 18 and 24.
- [Vercel Skills installer](https://github.com/vercel-labs/skills/blob/main/src/installer.ts)
  and [symlink regression tests](https://github.com/vercel-labs/skills/blob/main/tests/installer-symlink.test.ts):
  canonical copies, path containment, overlapping destinations and regression
  coverage; basis for 2–4, 7, 11–14 and 21.
- [Vercel Skills releases](https://github.com/vercel-labs/skills/releases): source
  symlink confinement and checking all destinations before writes; reinforces
  preflight validation and adversarial fixtures.
- [Vercel commands](https://github.com/vercel-labs/skills/blob/main/docs/commands.md):
  explicit check/update operations and installation modes; basis for 9, 15–17.
- [Cloudflare skill validation](https://developers.cloudflare.com/agents/skills/):
  client-side specification validation; basis for 1 and 9.

These are architectural comparisons, not evidence that upstream has every feature
below. Implementation and tests are original; no upstream code or skill prose is
copied. jstack deliberately keeps stricter source-link handling and project-only
installation, rather than adopting global modes or extra runtimes.

## Ranked improvements

| Rank | Improvement | Local evidence and intended outcome |
|---|---|---|
| 1 | Enforce metadata length bounds | Catalog lacks 64/1024 bounds; reject incompatible metadata (PR #2). |
| 2 | Reject source symlinks | `plan` reads linked files; prevent copying data outside the reviewed release. |
| 3 | Restrict manifest ownership | Manifest accepts arbitrary project-relative paths; prevent uninstalling unrelated files or project config. |
| 4 | Preflight ancestor collisions | Exact destination equality misses a managed file used as another path's parent; fail before writes. |
| 5 | Validate project config shape | Valid JSON scalars/arrays accepted as settings; require an object without rewriting user values. |
| 6 | Handle malformed doctor metadata | Non-object package JSON can raise AttributeError; return structured failed diagnostics. |
| 7 | Confine doctor metadata reads | Config/package symlinks can resolve outside the project; reject before reading. |
| 8 | Make text I/O explicitly UTF-8 | Default-encoding reads/writes affect non-ASCII fixtures, SEO adaptation and evidence. |
| 9 | Add standalone catalog validation | Frontmatter currently checked as part of install/tests; expose read-only validation with no target required. |
| 10 | Exercise macOS and current Python in CI | Linux-only 3.11/3.13 matrix misses native filesystem differences and Python 3.14. |
| 11 | Serialize mutations | Two installers can pass preflight concurrently; design a project-local lock with crash recovery. |
| 12 | Recheck paths during writes | Preflight cannot prevent concurrent symlink replacement; investigate descriptor-relative operations. |
| 13 | Persist interrupted transactions | In-process rollback cannot recover process termination; design a recoverable journal. |
| 14 | Expand rollback fault injection | Exercise chmod, symlink, config and manifest failures separately; prove exact restoration. |
| 15 | Offer JSON dry-run plans | Current human text requires parsing; expose deterministic changes/conflicts for automation. |
| 16 | Detect source-version drift in check | Integrity only checks installed hashes; separately report available source differences. |
| 17 | Report config and manifest separately | Distinguish integrity, customization and optional workflow readiness in check output. |
| 18 | Test exact metadata boundaries | Add 64/65 name and 1024/1025 description fixtures alongside existing rejection tests. |
| 19 | Bound external Git subprocesses | A hung Git command can stall root detection or SEO cloning; add actionable timeouts. |
| 20 | Add offline SEO preflight | Dry-run currently clones; separate local collision inspection from network validation. |
| 21 | Reject upstream SEO source links | Copytree follows symlinks; validate pinned dependency tree before staging. |
| 22 | Record SEO content integrity | Source commit is recorded but installed files lack hashes for later drift diagnosis. |
| 23 | Harden probe event shapes | Nested client payload assumptions can crash on schema drift; test malformed events. |
| 24 | Validate all local resource links | Current catalog check handles references paths only; consider scripts/assets without treating external URLs as local. |
| 25 | Document compatibility limits per provider | Preserve separate evidence for installed files, native discovery and authenticated runtime. |

## Acceptance

Every implementation PR runs `python3 -m unittest discover -s tests -v`, including
catalog frontmatter checks. New safety behavior gets adversarial regression tests.
Hosted checks must pass before merge. No target project installation, runtime,
service, deployment or user-level skill directory is changed by this batch.
