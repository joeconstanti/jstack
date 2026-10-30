# jstack

<div align="center">

![Made by Joe](https://img.shields.io/badge/Made%20by-Joe-red?style=for-the-badge)
![Agent Skills](https://img.shields.io/badge/Agent-Skills-orange?style=for-the-badge)
![Project Local](https://img.shields.io/badge/Scope-Project%20Only-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)

[![Checks](https://github.com/joeconstanti/jstack/actions/workflows/check.yml/badge.svg)](https://github.com/joeconstanti/jstack/actions/workflows/check.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

**Eleven composable workflows for maintaining web projects with coding agents. Install inside a project. Keep the same habits across stacks and tools.**

[Commands](#commands) • [Quick Start](#quick-start) • [Agent Support](#agent-support) • [Report Bug](https://github.com/joeconstanti/jstack/issues)

</div>

## Features

<div align="center">

| Feature | What it does |
|---------|--------------|
| **Project-only installation** | Writes inside an explicitly selected Git repository; refuses global destinations |
| **Shared skill source** | Canonical `.agents/skills/` files with provider discovery links and command adapters |
| **Eleven focused commands** | Sync, audit, edit, preview, check, review, verify and publish scoped work |
| **Stack discovery** | Reads project docs, scripts, lockfiles and CI rather than assuming a framework |
| **Existing tools respected** | Reuses local Claude SEO and Impeccable installations |
| **Reviewable updates** | Dry runs, file hashes, collision checks and a scoped uninstall |
| **Evidence-based results** | Separates build success, rendered behavior, pushed code and deployed outcomes |

</div>

## Commands

| Command | Outcome | Side effects |
|---------|---------|--------------|
| `/pull` | Fetch main and integrate it safely into the current branch | Local Git history; no push |
| `/audit [url]` | Run the relevant [Claude SEO](https://github.com/AgriciDaniel/claude-seo) audit and prioritize findings | Local reports; no automatic site fixes |
| `/edit [route]` | Enter [Impeccable Live Mode](https://github.com/pbakaus/impeccable) in the shared app preview | Local app/helper processes and requested source edits |
| `/preview [route]` | Start or reuse this checkout's server and open its app preview | Local development process |
| `/pr` | Topic branch, scoped commit, push and a problem-first PR; babysits it on request | Publishes a topic branch and PR; no merge |
| `/push` | Commit scoped work and push directly to main (typed only) | Publishes code; may trigger existing deployment CI |
| `/check` | Run relevant build, lint, syntax and test commands | Local check/build output |
| `/review [target]` | Grade bugs, regressions and scope creep as blocker, should or nit | Findings only |
| `/verify [route]` | Check rendered routes, responsive layouts and key interactions | Local browser evidence |
| `/doctor` | Diagnose skill integrity, discovery paths and project setup | Read-only diagnostics |
| `/update-skills` | Review and apply a project-local jstack update (typed only) | Managed skill files; retains local project config |

Commands are agent instructions, not new shell executables. **Codex uses `$pull`,
`$audit`, `$edit`, and so on.** Slash syntax varies by client; see Agent Support.
An agent may also discover and use the relevant skill from a natural-language
request, except `/push` and `/update-skills`: those fire only when typed
(`disable-model-invocation` for Claude Code and Cursor, `agents/openai.yaml`
policy for Codex). Publishing still requires the user's explicit intent.

Every skill first reads one shared file, `.agents/jstack/rules.md`. It holds the
context, scope, proof and outcome rules once, so each SKILL.md stays short. Its
proof ladder (stated, cited, ran, observed) is how every skill reports evidence.

A typical change can use `/pull` → `/preview` or `/edit` → `/check` → `/review` →
`/verify` → `/pr`. Each workflow also works on its own. `/push` is the direct-main
alternative when explicitly requested. These are separate steps, not an automatic
chain that silently publishes work.

## Technologies Used

<div align="center">

![Markdown](https://img.shields.io/badge/Markdown-000000?style=flat-square&logo=markdown&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)

</div>

| Technology | Purpose |
|------------|---------|
| **Markdown + SKILL.md** | Portable, readable workflow instructions |
| **Python 3.11+ standard library** | Installer, diagnostics and integration tests; no pip packages needed for jstack |
| **Relative symlinks** | Provider discovery without independent copies drifting |
| **Git** | Repository-root validation and workflow operations |
| **Optional GitHub CLI / connector** | PR creation and remote verification |
| **Optional SEO / Impeccable** | Specialist audit and live editing workflows |

## Project Structure

```text
jstack/
├── skills/                  # Eleven short SKILL.md workflows
│   └── doctor/scripts/      # Read-only installation diagnostics
├── shared/rules.md          # Context, scope, proof and outcome rules all skills read
├── install.py               # Project-only install / check / uninstall
├── setup-seo.py             # Optional pinned SEO instructions, no runtime setup
├── tests/                   # Installer integration and catalog checks
├── docs/
│   ├── inspiration.md       # Research decisions and upstream sources
│   └── rollout.md           # Initial six-project installation evidence
├── .github/workflows/       # Python test matrix
├── VERSION
└── LICENSE
```

Inside a target project:

```text
.agents/
├── skills/<command>/SKILL.md # Canonical installed skills
└── jstack/
    ├── rules.md             # Shared rules every skill reads first
    ├── manifest.json        # Version + hashes + owned paths
    ├── project.json         # Project-owned optional settings
    └── LICENSE
.claude/skills/<command>     # Links, or existing directory link retained
.cursor/skills/<command>     # Links
.cursor/commands/*.md        # Slash command adapters
.gemini/skills/<command>     # Links
.gemini/commands/*.toml      # Slash command adapters
.opencode/skills/<command>   # Links
.opencode/commands/*.md      # Slash command adapters
```

## Local Development

### Quick Start

Clone jstack **beside your projects**, then name the target repository explicitly:

```sh
git clone https://github.com/joeconstanti/jstack.git
cd jstack
git checkout v0.2.0
python3 install.py install --project /absolute/path/to/your-project --dry-run
python3 install.py install --project /absolute/path/to/your-project
python3 install.py check --project /absolute/path/to/your-project
```

Reload your coding agent to discover the files. In the target project, invoke
`/doctor` (Codex: `$doctor`), or run the diagnostic directly:

```sh
python3 .agents/skills/doctor/scripts/doctor.py --project .
```

The installer requires a Git repository root, never a home directory or global
skills folder. It preserves existing guidance, hooks, MCP configuration and other
skills. It checks the entire plan before writing, rejects collisions and modified
managed files, and rolls back file writes on an installation error. Empty parent
directories can remain after rollback or uninstall.

Installation does not commit or push the target project, start a web server,
install app dependencies, configure accounts or activate hooks. Commit the scoped
tooling changes in the target project when you want to share them with teammates.
Keep agent folders and runtime artifacts excluded from website deployment, especially
when FTP or another pipeline uploads the repository root.

### Agent Support

| Agent | Project-local discovery / invocation |
|-------|--------------------------------------|
| **Claude Code** | `.claude/skills/<name>/SKILL.md`; `/pull`, `/audit`, etc. |
| **Codex** | `.agents/skills/<name>/SKILL.md`; `$pull`, `$audit`, etc. |
| **Cursor** | `.cursor/skills/` plus `.cursor/commands/` slash adapters |
| **Gemini CLI** | `.gemini/skills/` plus `.gemini/commands/` TOML slash adapters |
| **OpenCode** | `.opencode/skills/` plus `.opencode/commands/` slash adapters |
| **Other coding agents** | Read the canonical SKILL.md directly, or use their supported project-local skill discovery |

The workflows use ordinary Markdown and adapt to the tools an agent has. This is
portable instruction support, **not a claim that every client has been exercised**.
Native command discovery, reload behavior, hooks and shared preview panes depend on
the agent's version. A client without a preview pane can use an available browser
or local URL; the skill reports that limitation instead of claiming a pane opened.
Symlinks must be supported and retained by your checkout. On Windows, use an
environment with Git symlink support and the required symlink privileges, or WSL.
The installer fails and rolls back if it cannot create the links.

### Specialist Dependencies

`/audit` routes to the installed **AgriciDaniel Claude SEO** skills. Existing
flattened (`.agents/skills/seo/`) and repository-layout
(`.agents/skills/claude-seo/`) installations are retained.

For a project without SEO skills:

```sh
python3 setup-seo.py --project /absolute/path/to/your-project --dry-run
python3 setup-seo.py --project /absolute/path/to/your-project
```

This installs MIT-licensed instructions and tools from commit
`6be93f45064ffbadced572b5d5c95f55fd263af0`, with its license and source record.
Plugin-root tokens in Markdown become project-relative paths. It creates discovery
links, does not overwrite existing SEO installations, and **does not install Python
packages, Chromium, extensions or credentials**. Follow the installed `/seo setup`
workflow when runtime setup is requested. Diagnose with its launcher `doctor --json`.

`/edit` routes to the installed **Impeccable Live Mode** skill and playbook. If absent,
use its versioned project installer from the target repository:

```sh
npx impeccable@4.8.0 install --providers=claude,codex,cursor,gemini,opencode,pi --scope=project --yes
```

Review that upstream installer's proposed changes and resulting diff. It may add
provider hooks and config; these belong to Impeccable's lifecycle, not jstack's
installer. Upstream: [Impeccable](https://github.com/pbakaus/impeccable), Apache-2.0.
Its launcher can download a platform engine on first use. Live Mode needs a local
source app and an actively serviced event loop. Stop and clean up instrumentation
before committing or deploying. jstack never injects Live Mode into production.

## Customization

Edit `.agents/jstack/project.json` in each target repository. The installer creates
only the minimal defaults and **never overwrites this file on updates or uninstall**.
For example:

```json
{
  "remote": "origin",
  "main_branch": "main",
  "site_url": "https://example.com",
  "dev_command": "npm run dev",
  "preview_url": "http://127.0.0.1:4321",
  "check_commands": ["npm run build", "npm test"]
}
```

These settings are hints for the agent, not shell commands the installer executes.
Keep secrets out of this file. Use project guidance for detailed conventions and
monorepo app selection. The shared skills infer missing settings from the repo;
static sites do not need a package.json or a new toolchain.

### Updates and Removal

Use `/update-skills` to review a tagged release, dry-run its installer and inspect
the resulting diff. To do it manually, check out a reviewed release in your jstack
clone and rerun the install command for the target project.

```sh
python3 install.py install --project /absolute/path/to/your-project --dry-run
python3 install.py install --project /absolute/path/to/your-project
python3 install.py check --project /absolute/path/to/your-project
python3 install.py uninstall --project /absolute/path/to/your-project --dry-run
python3 install.py uninstall --project /absolute/path/to/your-project
```

Modified managed files block updates and uninstall so they can be reconciled.
There is no force-overwrite switch. Project config, reports, unrelated tooling and
separately installed SEO/Impeccable dependencies remain after jstack removal.

## Contributing

<div align="center">

![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=for-the-badge)
[![Issues](https://img.shields.io/badge/Issues-Welcome-red?style=for-the-badge)](https://github.com/joeconstanti/jstack/issues)

</div>

| Step | Action |
|------|--------|
| **Branch** | Use a descriptive branch such as `fix/installer-collision` |
| **Change** | Keep skills concise, stack-aware and faithful to the user's scope |
| **Validate** | Run `python3 -m unittest discover -s tests -v`; skills must stay under 60 lines |
| **PR** | Explain the behavior change and provide actual validation |

Useful contributions include real cross-agent compatibility fixes, better stack
discovery and evidence-backed workflow improvements. Keep platform-specific tools
optional and avoid global installation paths or hidden publishing actions.

## Acknowledgments

<div align="center">

![Composable Workflows](https://img.shields.io/badge/Inspired%20By-Composable%20Workflows-purple?style=flat-square)
![Project Local](https://img.shields.io/badge/Built%20For-Project%20Local%20Agents-blue?style=flat-square)

</div>

- [t3dotgg/tstack](https://github.com/t3dotgg/tstack): focused workflows, composable handoffs and clear publication boundaries.
- [Cursor pstack](https://github.com/cursor/plugins/tree/main/pstack): project evidence, explicit stages and rendered verification before shipping.
- [Matt Pocock's skills](https://github.com/mattpocock/skills): concise composable skills and setup pointers only for genuine dependencies.
- [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo): specialist SEO audit dependency, MIT.
- [pbakaus/impeccable](https://github.com/pbakaus/impeccable): specialist visual editing dependency, Apache-2.0.
- [Made by Joe](https://github.com/madebyjoe/madebyjoe): README structure and presentation reference.

jstack's workflow instructions and installer are original. Upstream dependencies
retain their own licenses; they are not relicensed by jstack. See
[research decisions](docs/inspiration.md) for sources and reuse boundaries.

## License

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-green?style=for-the-badge)](https://github.com/joeconstanti/jstack)

</div>

jstack is available under the [MIT License](LICENSE).

---

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/joeconstanti/jstack?style=social)](https://github.com/joeconstanti/jstack/stargazers)

**Made by [Joe](https://madebyjoe.co)**

[GitHub](https://github.com/joeconstanti/jstack) • [Report Bug](https://github.com/joeconstanti/jstack/issues)

</div>
