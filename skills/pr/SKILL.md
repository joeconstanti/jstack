---
name: pr
description: "Create a named topic branch, commit scoped changes, push and open a detailed GitHub pull request. Use for /pr; does not merge or deploy."
---

# pr

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Inspect status, staged/unstaged diffs, branch, remotes and project conventions.
Identify the changes belonging to this request; never sweep in unrelated work or
stage everything. Exclude secrets, downloaded runtimes and live instrumentation.
Use an existing appropriate topic branch, or create a descriptive branch using
the repo convention (for example `feat/contact-form` or `fix/canonical-urls`).
Never use a `codex/` prefix. Do not rewrite an existing published branch.

Fetch the base branch. Review the scoped diff against it and bring main into the
topic branch when necessary, preserving unrelated work and published history.
Run the relevant check workflow; use rendered verification for UI changes when
supported. Report unavailable/failed checks accurately. If a check fails, fix
in-scope issues before publishing; don't label unverified changes ready.

Stage explicit paths or hunks. Preserve unrelated pre-staged work without
including it in this commit. Inspect the staged diff, commit, push with upstream
tracking, then create or update the PR using available GitHub tools or `gh`.
Honor a PR template. Lead with the problem and resulting behavior; describe why,
important implementation choices, actual validation, remaining limitations and
screenshots when useful. Write multiline bodies via a structured argument or
`--body-file`. Verify PR URL, base, head SHA and check state. Use harness-required
PR linking immediately after creation/push. Do not merge, enable auto-merge or
claim deployment. If GitHub access is unavailable, retain the local work and
report the exact remaining step. Return the PR link and verification summary.
