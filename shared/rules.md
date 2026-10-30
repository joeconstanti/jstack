# jstack rules

Every jstack skill reads this file before it starts. It holds the rules that all
of them share, so each skill can stay short.

## Context

- Project guidance (AGENTS.md, CLAUDE.md, CONTEXT.md, README, contributing
  notes) outranks these skills. Use its terms.
- `.agents/jstack/project.json` holds optional hints: remote, main branch, site
  URL, dev command, preview URL and check commands. A hint is not permission to
  widen the task. When a hint is missing, discover it from manifests, lockfiles,
  scripts and CI.
- Tool names differ between harnesses. Use the tool that does the job. Do not
  assume that a Claude, Codex, Cursor, Gemini or T3 API exists.
- When a step names another jstack skill, invoke that skill (or read its
  SKILL.md) instead of improvising its job.

## Scope

- The scope is what the user asked for. Keep unrelated dirty work, design,
  copy, routes and tracking IDs as they are.
- Make the smallest change that meets the request. Prefer deleting or narrowing
  code to new guards, options or helpers. Record other ideas as follow-ups.
- Publishing (push, PR, deploy, public comments) needs the user's explicit
  intent. Never force-push a shared branch, bypass branch protection or use
  `--admin`.

## Proof

Proof is evidence you observed in this session. Put each claim on this ladder
and say where it stopped:

1. **Stated.** Worth nothing alone.
2. **Cited.** A real `file:line`, config value or upstream source.
3. **Ran.** A command, test or script ran against the real code, with output.
4. **Observed.** The behavior was seen in the running app or on the live site.

A green build proves rung 3 for code, not rung 4 for UI. HTTP 200 is not a
rendered page. A push is not a deployment.

## Outcome

Give each step one result: passed, failed, not run or unavailable. Lead with the
outcome, then the evidence, then the gaps. Never invent counts, links, scores or
model names.
