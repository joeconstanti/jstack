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
