---
name: push
description: "Commit scoped work and push directly to the main branch when explicitly requested. Use for /push; inspect deployment triggers before pushing."
---

# push

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Treat an explicit /push request as authorization to publish the scoped changes
to main, subject to more specific user/project restrictions. Automatic skill
selection or an ordinary edit request alone does not authorize a push. Inspect
status, branch, staged and unstaged diffs, remotes, main and deployment workflows.
Mention known main-push deployment effects before the push; honor any instruction
to withhold deployment. Stop if publication conflicts with that restriction.

Run relevant checks and inspect the exact diff. Stage only request-owned paths
or hunks, excluding secrets and live instrumentation. Commit scoped changes if
needed. Preserve unrelated pre-staged work without including it in this commit.
Fetch main and inspect ancestry. On every branch, review the full outgoing commit
range and confirm that all commits belong to this request before pushing. On main, integrate only a safe
fast-forward; resolve divergence without force only when intent is clear. On a
topic branch, push HEAD to main only if it is a descendant of fetched main AND
the entire outgoing commit range belongs to this request. Otherwise preserve the
branch and explain what needs integration; never smuggle unrelated commits into
main. Use a normal non-force push to the explicit remote and main ref. Respect
branch protection; offer the PR route if direct push is rejected, without bypass.

Read back the remote main SHA and verify it matches the intended commit. Report
remote, branch, SHA and checks. A successful push is not proof of deployment or
live behavior. If deployment was requested, carry it through the project's
workflow and live verification using available tools; otherwise report triggered
CI/deployment state without claiming completion.
