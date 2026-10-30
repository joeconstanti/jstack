# Research and design decisions

Three separate GPT-6 Luna research agents, each with high reasoning effort,
inspected the requested repositories read-only on 30 October 2026. jstack uses
these ideas in independently written workflows and installer code; it does not
vendor their implementation or skill prose.

## t3dotgg/tstack

Sources: [README](https://github.com/t3dotgg/tstack/blob/main/README.md),
[full-send](https://github.com/t3dotgg/tstack/blob/main/skills/full-send/SKILL.md),
[file-pr](https://github.com/t3dotgg/tstack/blob/main/skills/file-pr/SKILL.md),
[babysit-pr](https://github.com/t3dotgg/tstack/blob/main/skills/babysit-pr/SKILL.md),
[license](https://github.com/t3dotgg/tstack/blob/main/LICENSE).
MIT, copyright Theo Browne, 2026.

Adopted:

- Small named workflows with natural-language discovery descriptions.
- A visible composition path, while each command remains independently useful.
- Project-specific preferences live in project guidance/config, not personal
  defaults baked into every shared skill.
- Check results, review findings, PR publication, merge and deployment remain
  distinguishable outcomes.
- Narrow deterministic helpers where they add reliability: jstack's installer
  and doctor own filesystem checks; the model owns project-specific decisions.

Adapted: provider-specific orchestration and watcher mechanics stay outside the
shared contract. A copied folder installer becomes a versioned project-local
manifest with collision checks, repeat installation, dry-run and uninstall.

## Cursor pstack

Sources: [README](https://github.com/cursor/plugins/blob/main/pstack/README.md),
[poteto-mode](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md),
[visual parity](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/visual-parity.md),
[shipping](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/shipping.md),
[setup](https://github.com/cursor/plugins/blob/main/pstack/skills/setup-pstack/SKILL.md),
[license](https://github.com/cursor/plugins/blob/main/pstack/LICENSE).
MIT, copyright Lauren Tan, 2026.

Adopted:

- Discover the project's actual stack, available tools and existing checks before
  choosing how to execute a workflow.
- State each workflow's expected evidence and finish conditions.
- Verify a rendered baseline against the requested change; a green build or CI
  result alone does not establish visual or interaction correctness.
- Reread external state before claiming publication succeeded: PR head/base and
  remote main SHA must be observed.
- Keep generated setup repeatable, with shared context separate from individual
  workflows and provider adapters.

Adapted: exact pixel equality belongs to an explicitly requested parity task,
not every edit. Cursor-specific orchestration is not required. Repeated setup
must preserve local customizations instead of replacing complete user configs.

## Matt Pocock's skills

Sources: [README](https://github.com/mattpocock/skills/blob/main/README.md),
[setup dependency ADR](https://github.com/mattpocock/skills/blob/main/.agents/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md),
[PR workflow](https://github.com/mattpocock/skills/blob/main/docs/engineering/pr.md),
[repository](https://github.com/mattpocock/skills).
Repository-level license: MIT, as inspected by the research agent.

Adopted:

- Focused SKILL.md entrypoints, with supporting code only when it is useful.
- Setup pointers only for real hard dependencies: audit routes to SEO, edit to
  Impeccable. Pull, review and other workflows do not require those integrations.
- Configuration-dependent skills read per-project settings; other skills can
  discover the repo and run without additional setup.
- Cross-agent portability means shared workflow intent plus concrete adapters,
  rather than assuming identical commands, tool names or browser capabilities.
- PR notes describe final behavior, actual verification and remaining risk.

Adapted: generic review and verification remain separate so users can request
one without authorizing publication or implementation.

## The five added commands

The research also suggested dedicated accessibility, performance, content,
assets, inspection and release-readiness skills. The initial release keeps the
five additions Joe approved: check, review, verify, doctor and update-skills.
They cover repeatable project maintenance without adding overlapping commands.
Focused accessibility/performance/content tasks can use the existing SEO and
Impeccable playbooks; new top-level commands can follow demonstrated need.

## Specialist integrations and licensing

- [Claude SEO](https://github.com/AgriciDaniel/claude-seo), MIT: audit reads the
  local upstream entrypoint and specialist playbooks. Existing copies are kept.
  Optional setup pins commit `6be93f45064ffbadced572b5d5c95f55fd263af0`, retains
  LICENSE, records the source and Markdown path adaptation, and keeps runtime
  installation separate. The copied plugin metadata is stored as
  runtime-plugin.json so the runtime uses manual/project-local layout.
- [Impeccable](https://github.com/pbakaus/impeccable), Apache-2.0: edit reads the
  installed live playbook. jstack neither copies its engine nor duplicates its
  live protocol. Its own versioned project installer owns its hooks and settings.

Any future copying of upstream code or substantial prose must retain the
corresponding copyright/license notices. Inspiration from workflow concepts is
not a redistribution of those implementations.

## Second pass, v0.2.0 (30 October 2026)

A second, line-by-line read of the three repositories (tstack `skills/*`,
pstack `poteto-mode`, `blast-radius`, `create-verification-skill`,
`principle-*`, and Matt Pocock's `writing-for-agents`, `invocation.md`,
`SCOPE.md` and `pr`). The rule for this pass: add only what changes agent
behavior, and remove more than is added. Net skill text fell from 380 to 345
lines, plus one 46-line shared file.

| Change | Source idea | Why it earns its place |
|--------|-------------|------------------------|
| One `rules.md` replaces a 7-line preamble copied into 11 skills | Matt: single source of truth, no duplication | One edit changes every skill; the skills now start with their own job |
| Proof ladder: stated, cited, ran, observed | pstack `blast-radius` "how sure are you"; tstack full-send "Proof" | One shared word for evidence strength in check, review, verify and pr |
| `/push` and `/update-skills` are typed-only | Matt `invocation.md`; pstack `disable-model-invocation` | Publishing and self-update can no longer fire from auto-discovery; zero context load |
| Review grades `blocker` / `should` / `nit` and flags scope creep | tstack `sol-loop` severities and budget | Findings rank by impact; review stops growing the diff |
| Review names the one safety fact and proves it | pstack `blast-radius` | A proven fact beats a long list of maybes |
| PR body: problem first, before/after evidence, one-way or two-way door | tstack `file-pr`; Matt `pr` (Merge Danger) | Reviewers see why and how risky before what |
| PR babysit section, used only when asked | tstack `babysit-pr` | One watcher, verify bot findings, decline scope creep in writing |
| Verify takes a baseline and checks side effects | pstack `create-verification-skill` proof standards | A final screenshot alone does not prove an interaction |
| Check separates new from pre-existing failures | tstack `sol-loop` "pre-failing checks" | A red check is not blamed on the change without evidence |
| Doctor reads skill names from the manifest | pstack "encode lessons in structure" | New releases need no doctor edit |
| Test: every skill points to rules.md and stays under 60 lines | pstack "encode lessons in structure"; Matt "sprawl" | The no-bloat rule is enforced, not hoped for |

Rejected, with reason:

- **New skills** (full-send, council, sol-loop, modernize, takeover, tdd,
  grilling). Matt's bar: if it composes from existing skills, it is not a new
  skill. These are general engineering flows that already ship as separate,
  better-maintained packs; jstack stays a web-maintenance set.
- **Router skill.** Eleven commands fit in the README table. A router adds
  context load for no gain at this size.
- **Bundled `pr-wait` watcher script.** Harness watchers (T3
  `watch_pull_request`) and `gh pr checks --watch` cover it without a
  stateful script in every project.
- **Model-specific delegation** (named reviewer models, multi-model panels).
  Harness- and account-specific; it belongs in personal AGENTS.md or CLAUDE.md.
- **Em-dash and prose style bans.** A style choice, not a behavior fix.
