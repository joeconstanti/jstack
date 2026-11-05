# v0.4.0 validation

5 November 2026. This report replaces assumptions about native client support
and adds observed behavioral evidence to the original source-inspection rubric.
It is not a claim of parity with specialist design or SEO tools.

## Research and method

Checked official [Codex skill documentation](https://developers.openai.com/codex/skills),
[Claude skills](https://code.claude.com/docs/en/skills),
[Cursor headless execution](https://cursor.com/docs/cli/headless),
[Gemini skill discovery](https://geminicli.com/docs/cli/skills/), and
[OpenCode skills](https://opencode.ai/docs/skills/). Documented paths and features
were treated as hypotheses to test in the installed clients, not certification.

Behavioral trials used fresh Claude Code 2.1.317 processes with the same synthetic
input and client defaults in both conditions. `modelUsage` consistently reported
`claude-sonnet-5-5` plus auxiliary `claude-haiku-5-5` activity. No model or effort
override was used. Safe mode, no tools, no MCP and no session persistence isolated
the instruction packet from local skills and hooks. The treatment added the
relevant jstack skill, shared rules and references; the control did not.

This tests source-based reasoning and writing, not automatic skill discovery,
rendered visual quality, real-world account operations or executing generated
code. Native discovery was checked separately. Each case has one answer per
condition per round: four development rounds (32 answers), followed by two fresh
holdout cases (four answers) after the changes were frozen.

A separate fresh, tool-free judge received A/B outputs and task text, without
condition labels, mappings or earlier results. It judged completion, factual
support, preserved intent and restraint. The parent randomized the labels;
neither generating process authored the mapping. This was context-blinded judging
by the same model family, not independent human review. Length counts use
`len(output.split())`, including Markdown table separators. Exact prompts,
outputs, label mappings and judgments are in [behavior.json](evidence/v0.4.0/behavior.json).
The first judge estimated counts; subsequent comparisons used measured counts.

## Development findings

| Case | Initial jstack / control words | Final jstack / control words | Final blind outcome |
|---|---:|---:|---|
| Research, 220-word cap | 208 / 190 | 214 / 208 | Tie |
| Writing, preserve commercial terms | 34 / 33 | 33 / 33 | Tie |
| Design critique, 220-word cap | 250 / 248 | 218 / 238 | jstack preferred: meets cap |
| Review, 250-word cap | 294 / 177 | 231 / 196 | jstack preferred: concrete findings and accurate Decimal qualification |

The initial judge preferred the control review; the other initial pairs tied.
Both initial design answers exceeded the cap. The first instruction change still
produced a 265-word review and 225-word design critique. A later review was 222
words, but its design counterpart remained over the cap. Those failures are
retained, not discarded or relabeled as successes.

Accepted changes:

- Remove the mandatory safety-fact and routine reporting appendix from review.
- Exclude speculative findings whose correction is “no change needed”.
- Keep proof and necessary qualifications inside the requested answer format.
- Leave a margin under hard word caps and combine related design observations.

These changes address observed failures without adding commands, dependencies,
services or an evaluation framework. Review is shorter than the original skill.
The final development result is selected after refinement on these prompts, so
it cannot establish general superiority or a stable success rate.

## Fresh holdout cases

No instructions were changed after these results.

| Case | jstack / control words | Blind outcome |
|---|---:|---|
| Contract + weighted-rate code review, 160-word cap | 167 / 143 | Control preferred: jstack exceeded the cap by seven words |
| A4 executive brief critique, 160-word cap | 158 / 151 | Tie |

Both reviews found the real defects, but the holdout shows that length compliance
remains unreliable. Both design answers preserved the supplied facts and identity
and labeled the lack of rendering. This mixed result is why the release does not
claim that jstack generally beats the control. Further tuning on this holdout
would stop it being a holdout; retain it and use new tasks for future evaluation.

## Native client smoke checks

Disposable Git projects contained the real installed catalog and a synthetic
proposal note. The probe invoked the writing workflow, read the note, preserved
its commercial qualifications and forwarded the marker `SMOKE-ARGO-19`.
Transcripts were inspected for reference loading, not merely exit status.
See [native.json](evidence/v0.4.0/native.json) for final outputs and read traces.

| Client | Version | Observed scope |
|---|---|---|
| Codex CLI | 0.166.0 | `$write` loaded project instructions, shared rules and editorial reference; proposal and marker returned |
| Claude Code | 2.1.317 | `/write` loaded project skill/reference and note; proposal and marker returned |
| Cursor Agent | 2026.10.22-27dcf5f | Workflow/reference loaded and proposal/marker returned; extra reporting after the final marker violated output formatting |
| Gemini CLI | 0.66.0 | All 14 project skills discovered; headless writing run timed out, so runtime unverified |
| OpenCode | 2.2.5 | Plain prompt returned prose without skill-loading proof; explicit native skill load failed, so native integration unverified |

Gemini discovery needed process-local `GEMINI_CLI_TRUST_WORKSPACE=true`; no
persistent trust or user settings were changed. Its initial untrusted list and
unsupported `--skip-trust` combinations are retained as failed attempts.
OpenCode's ordinary answer and an HTML response from a command-list probe were
not counted as native command success. No client or runtime was upgraded.
These are narrow CLI checks, not IDE menu/reload certification or proof that all
fourteen workflows work in every client. No publishing workflow was invoked as
a smoke test. The initial Cursor response appended reporting after the requested
final marker; the final-source recheck still did so. That formatting failure is
retained in the evidence and is not counted as a full task pass.

## Repeating the comparison

Use a disposable empty directory and the desired checked-out jstack source:

```sh
python3 docs/evidence/v0.4.0/run.py /absolute/path/to/empty-evaluation-directory
```

This invokes eight real Claude CLI requests, requires existing Claude
authentication and writes prompts, mappings, answers and raw CLI results only to
the chosen directory. It does not install anything or publish. Have a fresh
reviewer judge the anonymized task/answer pairs before opening `mapping.json`;
use the four criteria above and permit ties. The script repeats the four
original prompts; holdout prompts and results are retained in the evidence.

The original synthetic data can be public. Real client material must stay in a
private evaluation destination. Larger samples, independent human judgments,
rendered artifact comparisons and full client workflow certification remain
future work; this release does not promise those results.
