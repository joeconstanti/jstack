---
name: review
description: "Review scoped code changes for bugs, regressions and verification gaps. Use for /review; produces evidence-backed findings without automatic edits."
---

# review

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Determine the review target from the request: uncommitted changes, a commit
range, branch versus base, or PR. Inspect the complete scoped diff and enough
callers, config, tests and deployment context to assess behavior. Do not review
only file names or a generated summary. Follow project review conventions.

Prioritize reproducible correctness, security, broken routes, accessibility,
content/tracking regressions and data loss. Tie each finding to an affected file
and line, concrete triggering condition, impact and evidence. Distinguish confirmed
bugs from questions and missing verification. Don't demand unrelated refactors,
style churn or tests that merely mirror implementation. Use read-only checks or
isolated reproduction when helpful; do not alter the user's checkout or publish
comments unless asked.

Lead with findings by severity. If none, say no actionable findings were found,
then state reviewed scope, checks performed and remaining blind spots. Do not
claim absence of bugs. Keep review separate from implementation and merge approval.
