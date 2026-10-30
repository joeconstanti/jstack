---
name: update-skills
description: "Update the project-local jstack installation with a reviewed diff and preserve local customizations. Use for /update-skills; never installs globally."
---

# update-skills

Read the project's AGENTS.md and other applicable agent guidance first. Read
`.agents/jstack/project.json` if present; it contains optional project commands,
URLs and defaults, not permission to expand the task. Otherwise discover the
stack from the repository's docs, manifests, lockfiles and CI. Use the current
harness's tools and permission rules; adapt tool names rather than assuming
Claude, Codex, Cursor, Gemini or T3 APIs exist. Preserve unrelated dirty work,
existing design, copy, routes and tracking identifiers unless asked to change them.

Read `.agents/jstack/manifest.json` for installed version and managed paths.
Use https://github.com/joeconstanti/jstack as the source; fetch release/tag metadata
and inspect the selected release's changes before executing its installer.
Prefer a stable version tag, pin the resolved commit and tell the user the old and
new versions. Do not execute an unreviewed curl-to-shell pipeline.

Use a temporary clone outside the project. Read its README and installer, then
run `python3 install.py install --project <absolute-project-root> --dry-run`.
Review the proposed file list and collisions. If clean, run without --dry-run,
inspect the target diff, and run installer check plus the doctor skill. The
installer must retain project.json and unrelated skills/settings; modified managed
files or unmanaged collisions need resolution, not force overwriting. Keep that
resolution scoped and preserve the user's edits.

No global directories or whole-directory replacement. Never edit AGENTS.md,
CLAUDE.md, hooks, MCP settings or unrelated installed dependencies as an update
side effect. SEO and Impeccable have separate pinned/project-owned lifecycles;
report their versions but update them only when requested. Show the reviewable
diff and verified install version. Do not commit, push or deploy unless asked.
Clients may need a reload to discover updated skills; filesystem proof is not
proof that every agent has loaded them.
