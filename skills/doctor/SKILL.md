---
name: doctor
description: "Diagnose project setup, local dependencies and jstack skill installation without changing it. Use for /doctor or environment readiness issues."
---

# doctor

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Run `python3 .agents/skills/doctor/scripts/doctor.py --project .` from the
repository root. Inspect its report alongside README, project config and relevant
lockfiles. It checks installed jstack file integrity and discovery aliases,
configured commands, tool presence and SEO/Impeccable entrypoints. It does not
prove client reload, hook activation, runtime readiness, account access or app health.

For SEO runtime diagnosis use the installed claude-seo launcher doctor --json.
Do not use Impeccable doctor as a read-only substitute without inspecting its
playbook: upstream may repair state. Inspect config and launcher presence instead
unless a repair is requested. Check required tool versions against project docs.

Identify the smallest concrete repair and its scope. Do not install global tools,
modify credentials, activate hooks, upgrade dependencies or start services just
to make the diagnostic green. If the user requests repairs, perform the authorized
project-local changes and rerun the affected checks. Report ready, missing,
modified and unverified separately; never print environment secrets.
