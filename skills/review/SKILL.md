---
name: review
description: "Review a diff, branch or PR for bugs, regressions and scope creep, with proof for each finding. Use for /review or \"review this\"; reports findings and does not edit."
---

# review

Read `.agents/jstack/rules.md` first and apply it.

1. **Pin the target**: uncommitted changes, a commit range, branch against base
   (`git diff <base>...HEAD`) or a PR. Confirm the ref resolves and the diff is
   not empty. Find the intent (the user's request, the linked issue or PR
   body) and the standards (CONTRIBUTING, AGENTS.md, lint and style config).
2. **Read the whole diff**, plus enough callers, config, templates, tests and
   deploy rules to judge behavior. Look where grep stops: generated output,
   redirects and headers, sitemap and robots, analytics IDs, deploy filters.
3. **Find the safety fact.** Most risky-looking changes are safe because of one
   fact. Name it and push it up the proof ladder. A short script or an isolated
   reproduction beats a paragraph. Do not change the user's checkout or post
   comments unless asked.
4. **Grade each finding.**
   - `blocker`: the intended case is wrong, or data, security, routes or
     deployment break.
   - `should`: a real bug that users or callers will hit inside the intent.
   - `nit`: rare paths, small costs, style. Keep these few.
   Also flag scope creep: code, guards or tests that the intent does not need.
   Tag each finding `intent` (wrong or missing behavior) or `standards` (breaks
   a documented convention), so one kind does not hide the other.
5. **Report findings first**, by severity. Each finding gives `file:line`, the
   trigger, the impact, its proof rung and the smallest fix (prefer delete or
   narrow). Then give the scope reviewed, the safety fact and its rung, checks
   run and blind spots. With no findings, say "no actionable findings", not
   "no bugs".

A review is not implementation and not merge approval.
