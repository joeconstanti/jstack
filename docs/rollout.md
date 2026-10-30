# Initial rollout — 30 October 2026

jstack was published publicly to https://github.com/joeconstanti/jstack before
installation in the six requested web projects. All installations are local to
the target repositories. No global skill folders were changed.

## Verified installations

| Website | Project folder | jstack managed paths | Integrity check | Doctor |
|---------|----------------|----------------------|-----------------|--------|
| fromtheroot.studio | fromtheroot-web | 91 | Passed | Passed |
| automatedigital.ai | automate | 91 | Passed | Passed |
| syntheticlabs.xyz | syntheticlabs | 69 | Passed | Passed |
| madebyjoe.co | madebyjoe | 91 | Passed | Passed |
| joe.graphics | joegraphics | 91 | Passed | Passed |
| glasspane.xyz | glasspane | 58 | Passed | Passed |

Different path counts reflect existing whole-directory discovery symlinks. Every
project exposes all eleven skills in `.agents`, `.claude`, `.cursor`, `.gemini`
and `.opencode`, with Cursor, Gemini and OpenCode command adapters. Each project
has domain, source-server and check-command hints in `.agents/jstack/project.json`.
These hints were derived from existing guidance, package scripts and CI; no app
commands were run merely to install skills.

## Preserved and added tooling

- Existing SEO and Impeccable copies, agent settings, hooks and guidance were kept.
- Made By Joe lacked SEO skills, so the optional pinned Claude SEO installer added
  them with its MIT license, source commit record and project-relative paths.
  Python dependencies and Chromium were not installed.
- All pre-existing dirty paths in Synthetic Labs and joe.graphics were compared
  against a pre-install content/symlink snapshot and remained unchanged.
- Glasspane's FTP deployment exclusions gained `.opencode/**` so the new adapters
  cannot be uploaded with its root-based site deployment.
- The target installations, project settings, dependency files and Glasspane
  exclusion are uncommitted local changes. No target repository push, PR or
  website deployment was performed.

## Validation and limits

- Fourteen Python integration/catalog tests passed locally. They cover repeat
  installation, uninstall, config preservation, unmanaged collisions, modified
  managed files, external symlinks, provider-specific directory links, TOML
  parsing, rollback on a simulated filesystem failure and existing SEO retention.
- All eleven SKILL.md files passed the skill-creator frontmatter validator.
- A fresh temporary project installation and pinned SEO install passed. SEO's
  runtime doctor reported manual mode and missing runtime dependencies, as
  expected; no user-level fallback runtime was created.
- GitHub's initial Check jstack workflow completed successfully on Python 3.11
  and 3.13: [run](https://github.com/joeconstanti/jstack/actions/runs/41056964699).
- Installation integrity verifies file hashes, executable bits and discovery links.
  Doctor also checks dependency entrypoints. Neither proves client reload,
  hook activation, account authentication, rendered UI or deployment health.

Reload the coding agent in a target project, then invoke `/doctor` or Codex's
`$doctor`. Use `/preview` and `/edit` (Codex `$preview` and `$edit`) when a real
preview/live-edit session is wanted. This rollout did not start those sessions.

## Update to 0.2.0 — 30 October 2026

The six projects were updated in place from this checkout with `install.py`.
Each dry run showed 48 changes and no collisions or modified managed files.

| Website | Project folder | Managed paths | Integrity check | Doctor | Other Git state |
|---------|----------------|---------------|-----------------|--------|-----------------|
| fromtheroot.studio | fromtheroot-web | 94 | Passed | Passed | Unchanged |
| automatedigital.ai | automate | 94 | Passed | Passed | Unchanged |
| syntheticlabs.xyz | syntheticlabs | 72 | Passed | Passed | Unchanged |
| madebyjoe.co | madebyjoe | 94 | Passed | Passed | Unchanged |
| joe.graphics | joegraphics | 94 | Passed | Passed | Unchanged |
| glasspane.xyz | glasspane | 61 | Passed | Passed | Unchanged |

"Unchanged" means `git status --porcelain` and `git diff` hashed the same before
and after the update. The three new managed paths per project are
`.agents/jstack/rules.md` and the Codex `agents/openai.yaml` policies for `push`
and `update-skills`. Existing deploy exclusions (`.agents/**`, `.claude/**`, and
the other provider folders) already keep them out of FTP and rsync uploads.
project.json files were kept. The installations remain uncommitted local
changes; nothing was pushed or deployed, and no agent was reloaded.
