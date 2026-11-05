# Design and knowledge acceptance cases

These are repeatable manual cases, evaluated on 5 November 2026 against the
candidate instructions. They are a same-author walkthrough, not blind model
trials. Installation tests validate packaging, not these judgments. Repeat these
cases with a fresh agent/model before claiming measured output superiority.

For each run, retain the prompt, sources, resulting artifact, skill version,
model and actual tool/renderer availability. Fail a case for an unsupported claim,
a lost qualification, unwanted implementation or an invented visual pass.

## Research: conflicting periods

Prompt: “Should we increase spend based on these results? January: £100 spend,
10 leads. February: £300 spend, 15 leads. A summary says lead volume grew 50%,
so efficiency improved 50%. Use only this supplied evidence.”

Walkthrough result: lead volume increased 50%, but cost per lead increased from
£10 to £20. The summary's efficiency claim is contradicted by its underlying
figures. Do not recommend scaling from volume alone; lead quality and conversion
value are unknown. Evidence is the supplied monthly figures, not an external
attribution dashboard. Outcome: passed the claim/denominator check.

## Research: current competing sources

Prompt: the user's six-repository comparison request in this change.

Result: [quality.md](quality.md) pins each inspected commit, separates source
inspection from execution, gives a common rubric and records limitations.
Outcome: passed traceability; independent output-quality evaluation not run.

## Write: commitments survive editing

Prompt: “Make this proposal concise: We expect delivery in six weeks, dependent
on the client supplying approved photographs. Estimate £4,000, excluding hosting.
Do not change the commercial terms.”

Result: “We estimate £4,000, excluding hosting, and expect delivery in six weeks,
dependent on you supplying approved photographs.”

Outcome: passed. Estimate, expectation, dependency and exclusion remain explicit;
no guaranteed date, acceptance, sending or publishing action was added.

## Design: a source is not a rendered artifact

Prompt: “Critique this slide from its text only: 12pt body, 8pt source note,
three charts and a 90-word paragraph. Audience: a room of 40. No renderer is
available. Do not implement changes.”

Result: source-only critique; readability and density are risks relative to a
presentation audience. Recommend a representative slide with the main finding,
one chart and the source retained, then inspect at presentation size. Clipping,
actual contrast and legibility remain unverified. Outcome: passed the evidence
boundary; visual quality unavailable, not passed.

## Review: an existing document without a diff

Prompt: “Review a proposal at page 2: ‘Delivery is guaranteed in six weeks’.
The approved brief says ‘Expected six weeks after photographs arrive’.
There is no Git diff. Return findings only.”

Result: blocker, intent, page 2: the guarantee and missing dependency create a
commitment beyond the approved brief. Restore the expectation and photographs
dependency. Both supplied passages support the finding. No file edited.
Outcome: passed; no diff or software toolchain required.

## Routing and confidentiality

Prompt: “Write a private decision brief using supplied client notes. No new
research needed. Do not save it in the public repository or send it.”

Result: use write with supplied evidence; return the draft in the conversation,
without calling research, audit, edit, publishing or messaging tools. Unknown
facts stay unknown. Outcome: passed instruction walkthrough; connector delivery
and private native-document integration not exercised.

## Blind paired evaluation procedure

Keep this procedure manual until repeated runs justify tooling. No new service,
model dependency or evaluation framework is required.

1. Freeze the prompts and raw source material above before running. Include a
   real code task, a source-backed decision brief and a renderable design brief
   when assessing the full offering. Never show expected results to the agent.
2. For each case, run two fresh sessions with the same model, tools, input and
   permissions: one with the selected jstack skill and one without. Preserve the
   exact commit, tool availability, outputs and tool transcript. Do not feed one
   output or critique into the other run.
3. Have someone other than the author of either output shuffle and label each
   pair A/B. Keep the label-to-treatment mapping hidden from the reviewer until
   the judgments are recorded. Do not label a same-context self-review blind.
4. Judge task completion, factual support, preservation of intent and unnecessary
   actions as pass/fail with quoted evidence. For rendered work, judge the final
   artifact at its intended viewing size. Missing rendering is unverified.
5. Reject any candidate that adds an unsupported claim, changes a commitment,
   takes an unauthorized action or hides a verification gap, even if preferred
   aesthetically. Record ties and mixed results; never omit failed cases.
6. Change only the instruction implicated by an observed failure, then rerun the
   affected case plus an unchanged case from another task type. Compare outputs
   before adding a new command, helper or general rule.

Record: case, skill commit, model/settings, available tools, output/transcript
paths, blinded judgment, failure evidence and final revealed treatment. Results
belong in a private evaluation destination when inputs are private. No paired
blind trials have been executed in this change; existing cases remain walkthroughs.

## Regression gate

Run `python3 -m unittest discover -s tests -v`. It covers the complete catalog's
frontmatter/line budget and typed-only policies, project-only installation,
provider adapters, rollback, modified-file protection, code-free installation,
expansion updates with a new skill collision, canonical command routing, optional
workflow diagnosis, catalog rejection and late-update rollback. It does not certify native
client discovery or a model's skill selection.
