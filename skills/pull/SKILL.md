---
name: pull
description: "Bring the latest main branch into the current checkout without losing local work. Use for /pull or updating a working branch from main."
---

# pull

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Inspect status, current branch, upstream and remotes. Determine the main branch
from project config or the remote default; prefer the configured remote, otherwise
`origin`. Fetch that remote. Do not reset, clean, auto-stash or change branches
with unrelated work. If uncommitted files could be affected, stop before merging
and explain which files need handling.

On main, fast-forward only (`git merge --ff-only <remote>/<main>`). On a topic
branch, merge the fetched main into the topic branch, retaining published history;
follow an explicit project rebase convention only when compatible with the user's
instructions. Inspect divergence first. If main has diverged, report it rather
than inventing a resolution. On conflicts, preserve both sides; resolve only when
intent is clear, otherwise identify the files needing a decision. Never push as
part of pull. Report branch, resulting SHA and merge/fast-forward state.
