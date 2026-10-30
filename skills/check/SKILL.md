---
name: check
description: "Run the relevant project build, lint and tests and report real results. Use for /check or checking whether scoped changes are ready."
---

# check

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Discover documented checks from project config, package scripts, CI and the
changed files. Inspect what each command does before running it: a script named
check or build can have side effects. Respect package manager and lockfile; don't
add a toolchain to a static project merely to create a green result.

Choose checks that cover the actual change: syntax/types, lint, meaningful tests,
build, route/assets validation as applicable. Respect dependencies between checks
and use parallel execution only for independent commands. Do not run deployment,
fix mode, blanket formatting or dependency upgrades as a side effect. A build may
regenerate tracked files; inspect and report those without overwriting unrelated
work. Fix task-owned failures if authorized, then rerun the affected check.

Return commands and exit results, what they cover and any blocker. Distinguish
passed, failed, not run and unavailable. Do not invent test counts or call a build
browser validation. Use verify for rendered routes and interactions.
