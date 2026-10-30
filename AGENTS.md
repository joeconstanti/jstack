# jstack development

This repository distributes project-local, cross-agent workflow skills. Keep the
installer project-only and collision-safe. Never write to user-level skill folders.
Use standard-library Python for installation and diagnostics. Preserve existing
agent settings, skills, hooks and project guidance. Run `python3 -m unittest discover
-s tests -v` and validate skill frontmatter before publishing. Do not copy upstream
skill prose or code without retaining its license and attribution. Installation
must not start services, install runtimes, commit target repositories or deploy sites.
