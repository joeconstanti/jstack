---
name: verify
description: "Verify rendered routes, responsive layouts and key interactions for the scoped web changes. Use for /verify or browser acceptance checks."
---

# verify

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Use the preview workflow to identify the correct checkout and app, then inspect
the routes affected by the change and key shared navigation. Use existing browser
QA scripts when appropriate and the current harness's permitted browser tools.
If browser inspection is unavailable, report the missing evidence rather than
substituting HTTP 200 as a visual pass.

Check representative desktop and narrow mobile widths, loading/empty/error states
relevant to the change, console/network failures, internal links, keyboard focus
and the main user action. Let fonts, images and animations settle before comparing
layout. Compare against supplied references or the unchanged baseline; preserve
identity and routes. Avoid submitting real leads, sending messages, purchasing or
changing account data without authorization; use a safe test path when provided.

Record the exact URL, viewport, scenario and observed result; save evidence under
`.agents/jstack/reports/verify/` or the user's chosen location. Separate source,
built output, live deployment and authenticated analytics proof. HTTP tracking
transport is not account attribution. Report failures and gaps; fix only when
implementation is authorized. Verification itself does not publish or deploy.
