---
name: review
description: "Review code, designs or documents for defects, unsupported claims and scope creep, with evidence for each finding. Use for /review or \"review this\"; reports findings and does not edit."
---

# review

Read `.agents/jstack/rules.md` first and apply it.

1. **Pin the target**: named artifacts, uncommitted changes, a commit range,
   branch against base (`git diff <base>...HEAD`) or a PR. For a diff, confirm
   the ref resolves and the diff is not empty. For an artifact, identify its
   version and audience; no Git diff is required. Find the intent (request,
   issue or PR body) and applicable project conventions.
2. **Read the whole artifact or diff**, plus enough relevant context and tests to
   judge behavior. For code, look where grep stops: generated output,
   redirects and headers, sitemap and robots, analytics IDs, deploy filters.
   For prose, trace material claims to sources, check logic and commitments.
   For design, compare with the brief and inspect the rendered artifact when
   available; distinguish observed defects from aesthetic preferences.
3. **Find the safety fact.** Most risky-looking changes are safe because of one
   fact. Name it and push it up the proof ladder. A short script or an isolated
   reproduction beats a paragraph. Do not change the user's checkout or post
   comments unless asked.
4. **Grade each finding.**
   - `blocker`: the intended case is wrong, or data, security, routes or
     deployment break, or the central claim/decision is unsupported.
   - `should`: a defect that affects users or readers inside the intent.
   - `nit`: rare paths, small costs, style. Keep these few.
   Also flag scope creep: code, guards or tests that the intent does not need.
   Tag each finding `intent` (wrong or missing behavior) or `standards` (breaks
   a documented convention), so one kind does not hide the other.
5. **Report findings first**, by severity. Each gives a `file:line`, page/slide
   or source passage, trigger, impact, proof rung and smallest fix (delete or
   narrow). Then give the scope reviewed, the safety fact and its rung, checks
   run and blind spots. With no findings, say "no actionable findings", not
   "no bugs".

A review is not implementation and not merge approval.
