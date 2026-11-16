---
name: start
description: "Onboard a new project: discover what the user wants to build, choose a coherent stack and publishing plan, then scaffold the first working flow. Use for /start or project setup from scratch; ordinary edits use existing workflows."
---

# start

Read `.agents/jstack/rules.md` first and apply it.

1. **Locate the project.** Inspect guidance, files, Git state, manifests and
   existing setup decisions. Treat a nonempty project as an existing system;
   retain its stack unless migration was requested. Outside a repository,
   establish the intended directory before creating anything. This skill sets
   up an app; installing jstack itself remains the project-only installer's job.
2. **Run a mini onboarding.** Start with “What are you building, who is it for,
   and what should someone be able to do first?” Reuse answers already given.
   Ask at most three related questions per round, in plain language with a
   recommended option where useful. Resolve only decisions that change setup:
   site/app/platform, required data/auth/payments/content editing, visual
   references, team familiarity, and hosting/budget constraints. Do not make
   users choose libraries before understanding their needs. Wait for answers;
   if they ask you to choose defaults, state those and proceed.
3. **Choose one coherent recipe.** Read `references/recipes.md` beside this
   file. Recommend a framework, component system, styling, package manager,
   data services when needed, and compatible publishing target. Explain why
   each fits; offer one alternative only for a consequential tradeoff. Verify
   current official scaffolding and host compatibility before running commands.
   Summarize the chosen setup and first working flow; ask only about unresolved
   consequential choices, not decisions the user has already delegated.
4. **Record and scaffold.** Save the goal, first flow, recipe, design choices,
   selected versions/template source, local commands, deployment plan and open
   decisions in existing project docs, or `docs/project-setup.md` if none fit.
   Scaffold in a temporary sibling directory when a generator requires an empty
   destination, inspect its output and copy only nonconflicting app files.
   Keep one lockfile and component system. Install app dependencies with the
   existing runtime; report a missing runtime rather than silently installing it.
   Add environment-variable names and placeholders, never credentials. Configure
   only requested local publishing files; account creation, paid resources,
   remote repositories, pushes and deployment need explicit user intent.
5. **Prove the starting point.** Implement the smallest representative flow
   with the chosen components and realistic states. Use the check skill for
   available build/lint checks and verify for rendered acceptance. Distinguish
   mocks from connected services. Document setup gaps and hosting prerequisites;
   a deploy config is not a deployed app. Update project command hints only
   with observed commands, preserving unrelated settings.
6. **Hand over** the recipe and rationale, changed files, run/check commands,
   evidence and the next product step. On rerun, resume the saved choices and
   fill gaps rather than re-interviewing or regenerating the project.
