---
name: audit
description: "Audit website SEO using the project-local AgriciDaniel Claude SEO skills. Use for /audit; this produces findings rather than automatic site edits."
---

# audit

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Locate the installed SEO entrypoint: `.agents/skills/seo/SKILL.md`, or
`.agents/skills/claude-seo/skills/seo/SKILL.md`. Read it and the relevant
`seo-audit/SKILL.md` for a full site, `seo-page` for one page, or `seo-technical`
for a technical-only request. Source: https://github.com/AgriciDaniel/claude-seo.
If absent, report the missing dependency and use the pinned project-local setup
in jstack's README; never silently install global tools.

Choose the target from the request, then configured `site_url`, then verified
repository metadata. Distinguish local source, rendered local output, deployed
HTTP behavior and authenticated account evidence. Start with the installed
runtime's `doctor --json` when bundled scripts are needed. Map upstream
`${CLAUDE_PLUGIN_ROOT}` paths to the actual local installation (repo layout:
`.agents/skills/claude-seo`; flattened layout: launch from
`.agents/skills/seo/scripts/claude-seo`). Keep runtime data project-local: if a
plugin-layout launcher would use a
user-level fallback, pass `CLAUDE_SEO_DATA_DIR` pointing to this project's
`.agents/jstack/runtime/seo` on its runtime commands. Follow the installed
runtime's setup
rules; missing dependencies or account access are limitations, not scores of zero.

Apply upstream crawl bounds and robots behavior. Use available specialist skills;
only delegate when allowed by the current harness and user. Otherwise do the
specialist passes in context. Record evidence, affected URLs, severity, confidence
and actionable fixes. Do not invent ranking promises, field CWV, traffic, schema
claims or account attribution. Save reports under `.agents/jstack/reports/audit/`
unless the user specifies another destination; do not publish or fix the site
unless asked. Report coverage and skipped checks alongside priorities.
