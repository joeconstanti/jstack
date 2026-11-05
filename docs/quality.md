# Comparison and quality improvement record

Inspected 5 November 2026. This is a source-backed editorial assessment of the
offering, not a benchmark of competing models or generated artifacts. Upstream
runtimes and test suites were not executed. Stars and README test counts do not
contribute to scores. The rubric is a retrospective design audit; it was not
preregistered before implementation. No independent evaluator participated in
this original source assessment.
Later context-blinded model trials are recorded in [v0.4.0 validation](release-0.4.0.md).

## Sources and scope

Read repository READMEs, licenses, skill inventories and the representative
instructions below from shallow checkouts. Links pin the exact snapshots.

| Repository | Snapshot and representative instructions | License |
|---|---|---|
| tstack | [`1085050`](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af), `skills/full-send/SKILL.md` | MIT |
| pstack | [`2776ddd`](https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack), `skills/poteto-mode/SKILL.md`, `playbooks/hillclimb.md`, `skills/technical-writing/SKILL.md` | MIT |
| gstack | [`641d622`](https://github.com/garrytan/gstack/tree/641d62291c510954d30d967b2c6fc0c785a6d37f), `office-hours/SKILL.md`, `plan-design-review/SKILL.md`, `document-release/SKILL.md` (selected sections) | MIT |
| Impeccable | [`c8891a9`](https://github.com/pbakaus/impeccable/tree/c8891a9ae865d6ee311836ae5199bfce0fe115b1), `.agents/skills/impeccable/SKILL.md`, `reference/critique.md` | Apache-2.0 |
| taste-skill | [`9b4bf93`](https://github.com/leonxlnx/taste-skill/tree/9b4bf937a1f69348126959c15d2f99a73e65699b), `skills/taste-skill/SKILL.md` | MIT |
| Claude SEO | [`6be93f4`](https://github.com/AgriciDaniel/claude-seo/tree/6be93f45064ffbadced572b5d5c95f55fd263af0), `skills/seo-content-brief/SKILL.md` | MIT |

jstack baseline: local v0.3.0 catalog of eleven workflows at the start of this
change. Working tree was clean. Candidate: this source change, not a tagged release.
No upstream prose, implementation or assets were copied into this change.
Existing SEO setup retains its upstream license and pinned source record.

## Rubric

Six equally weighted dimensions, each 0–4; total /24. These are coarse judgments,
not interval measurements: a one-point difference is not proof of superiority.
Use the per-dimension profile, not the total, to choose a tool.

- **Workflow:** discoverable entry, clear boundaries and useful handoffs.
- **Depth:** concrete domain decisions and failure handling within declared scope.
- **Evidence:** explicit acceptance, observed results and honest uncertainty.
- **Safety:** installation/mutation boundaries and preservation of existing work.
- **Portability:** explicit discovery/adapters and optional-tool fallbacks.
- **Validation:** inspectable tests, examples and an evaluation method.

Common anchors: 0 absent; 1 mostly aspiration; 2 useful instructions with gaps;
3 concrete contract and supporting mechanisms; 4 unusually comprehensive
mechanisms and documented coverage. Scores judge inspected design, not verified
execution of upstream mechanisms. Portability does not imply client certification.

## Assessment

| Offering | Workflow | Depth | Evidence | Safety | Portability | Validation | /24 |
|---|---:|---:|---:|---:|---:|---:|---:|
| tstack | 3 | 3 | 4 | 2 | 2 | 2 | 16 |
| pstack | 4 | 4 | 4 | 2 | 2 | 3 | 19 |
| gstack | 4 | 4 | 4 | 2 | 3 | 4 | 21 |
| Impeccable | 4 | 4 | 4 | 3 | 4 | 4 | 23 |
| taste-skill | 3 | 4 | 4 | 2 | 3 | 3 | 19 |
| Claude SEO | 4 | 4 | 4 | 3 | 2 | 3 | 20 |
| jstack baseline | 3 | 2 | 3 | 4 | 3 | 2 | 17 |
| jstack candidate | 3 | 3 | 3 | 4 | 3 | 3 | 19 |

The final baseline gives existing code workflows credit for domain depth (2/4),
correcting the provisional 1/4 used during the first pass. This raises the
baseline from 16 to 17; the candidate score remains 19.

Score rationale and limits:

- **tstack:** compact compositions and strong runtime/merge gates; installation
  examples copy to global folders. Multi-provider review has real prerequisites;
  a less extensive inspected validation surface than specialist toolchains.
- **pstack:** deep task playbooks, writing guidance, explicit premise testing and
  a disciplined hillclimb/eval method. Cursor-centric integrations and global
  model configuration reduce fit with jstack's project-only portability goal.
- **gstack:** strong discovery-to-decision artifacts, alternatives and cross-stage
  handoffs, plus host tiers/certification documentation. Global state, hooks,
  runtimes and auto-update/team setup are a broader operational commitment.
- **Impeccable:** rich design vocabulary, medium/context selection, critique and
  detector evidence with documented test fixtures and broad provider support.
  Engine/helper lifecycle makes this deeper than portable prose alone.
- **taste-skill:** concrete visual system, assets and browser/performance checks.
  Its strong site-specific prescriptions and Node/browser prerequisites narrow
  applicability; default asset copying is unsuitable for some incumbent systems.
- **Claude SEO:** detailed specialist routing, report formats, per-claim/content
  rules and optional live-data integrations. Runtime and Claude-centric agent
  structure need setup; jstack already reuses it rather than recreating it.
- **jstack baseline:** excellent project-local collision/rollback safeguards,
  short entrypoints and provider adapters, but design is only Live Mode and
  general research/writing is absent. Installer tests do not test output quality.
- **jstack candidate:** distinct core design/research/writing contracts, medium
  acceptance criteria and worked evaluation cases close the most material scope
  gaps. Same-author walkthroughs justify only a limited validation improvement.
  No new engine, independent trials or host certification: those scores stay low.

The candidate reaches the same coarse total as pstack/taste-skill on this rubric,
but does not establish equivalent design output or specialist depth. Impeccable
and gstack remain stronger reference points for runtime/evaluation investment.

## Hillclimb decisions

| Pass | Observed gap | Accepted change | Evidence |
|---|---|---|---|
| Baseline | No knowledge workflow; design requires Live Mode | Establish the six-source comparison | Eleven-entry catalog and original descriptions |
| 1 | Missing distinct work capabilities | Add research, write and design with focused references | All three frontmatters validate; each entry stays below 60 lines |
| 2 | Review demands a diff; verify demands an app | Accept standalone artifact reviews and document/slide verification; extend shared evidence rules | Document and no-renderer walkthroughs in evaluation.md |
| 3 | Broader catalog could collide during updates | Add code-free install and catalog-expansion integration tests | CLI install/check/uninstall and failed-update preservation exercised |

Rejected: cloning specialist prose, asset systems or browser engines; adding
separate brainstorm, proposal, critique, summary and knowledge-capture commands
that compose from these capabilities. The installer remains standard-library
Python with no new runtime or global writes.

## Acceptance and remaining work

Local acceptance: the three distinct capabilities have useful contracts and
references; document workflows do not require app setup; every skill stays at
or below 60 lines; existing publication policies remain; required tests and frontmatter
validation pass. See [evaluation cases](evaluation.md) for actual walkthroughs.

This completes the local capability improvement, not empirical parity with the
best specialists. The [release validation](release-0.4.0.md) now records real
model trials and client discovery runs. Blind rating of rendered outputs and
broader real briefs remain useful next steps. Preserve those raw outputs and evaluate factual accuracy, task completion and visual usability with
the same inputs before raising scores. Native document/browser behavior and
upstream runtime quality remain unverified here.

## Reliability follow-up

Command adapters now load the canonical skill, preserving the base directory for
skill-local references and avoiding three copies of every workflow body. Catalog
preflight rejects invalid frontmatter, missing local references and inconsistent
invocation policies before target writes. Doctor separates optional audit/edit
instruction availability from core integrity; runtime readiness stays unverified.
Malformed-manifest and late-update rollback tests protect the update boundary.
Generic writing instructions were trimmed; the command count remains fourteen.
The evaluation document now includes a blind paired procedure, with subsequent
trials and limitations recorded in the release validation report. These changes do not increase the subjective score.
