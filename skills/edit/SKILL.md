---
name: edit
description: "Start Impeccable Live Mode for visual editing in the shared app preview. Use for /edit or an interactive local design session."
---

# edit

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Read the installed `.agents/skills/impeccable/SKILL.md` (or provider-specific
copy) and its `reference/live.md`. This command means `/impeccable live` in
supporting agents or `$impeccable live` in Codex. Source:
https://github.com/pbakaus/impeccable. If absent, report the dependency and the
project-local installation path in jstack's README; do not substitute a redesign.

Use the preview skill's server discovery to locate the local SOURCE app. Reuse a
server only after confirming it serves this checkout. Follow Impeccable's context,
live boot and target selection, then open the returned app route in the harness's
shared preview pane. The helper port is not the app port. If no shared preview
exists, use an available browser and explain the limitation; do not claim the
preview pane opened. Never inject into production or weaken production CSP.

Service the live event loop through the harness's supported foreground/background
mechanism, following the installed playbook within higher-priority harness rules.
Keep listening while live mode is active; starting a helper alone is not a working
edit session. Generate variants within the current identity unless a redesign is
requested. On interruption, use live-status/live-resume before guessing. On exit,
follow upstream cleanup and verify injections, variant wrappers and temporary
instrumentation are removed. Keep source edits separate from runtime records;
never commit or deploy active instrumentation.
