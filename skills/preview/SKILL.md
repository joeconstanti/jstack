---
name: preview
description: "Open the current local website or app in the coding agent shared preview pane. Use for /preview; supports static and framework projects."
---

# preview

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Determine the requested app/route, source root, start command and URL from
project config, docs, package scripts and framework config. Prefer the source dev
server for editing; label production-build previews clearly. Respect lockfiles
and package-manager choice. Static sites can use a loopback-bound Python server
when there is no documented server; do not pretend it implements Apache redirects,
headers or production CSP.

Check existing preview tabs and listeners using supported tools. Probe a known
URL and verify the responding process/root belongs to this checkout before reuse.
Do not kill another project's server or assume a busy default port is this app.
Use a free port and keep the process in a harness-managed terminal/session if a
server must start. Record the command, cwd, session and actual URL. Do not install
dependencies blindly when the project needs setup; diagnose the missing pieces.

Use the current harness's shared preview/browser tools. In T3, call preview_status
first and use preview_open when needed. Follow current harness browser policy.
Open the requested route and check an actual rendered state and console/network
errors where supported. HTTP readiness alone does not prove a rendered preview.
If no shared preview capability exists, use an available browser or provide the
local URL and explicitly state the limitation. Report URL, source/build mode and
whether the pane actually opened. Keep a requested preview available for the user.
