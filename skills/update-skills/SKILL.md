---
name: update-skills
description: "Review and update jstack and its imported skills in this project. Typed only, never picked automatically."
disable-model-invocation: true
---

# update-skills

Read `.agents/jstack/rules.md` first and apply it.

1. **Current state.** Read `.agents/jstack/manifest.json` for the installed
   version, upstream commits and managed paths.
2. **Pick a revision.** Source: https://github.com/joeconstanti/jstack. Use the
   latest stable tag with `--refresh-imports` support, or use `main` if no tag
   supports it. Pin the jstack commit and review its changes. Never pipe a
   download into a shell.
3. **Dry run.** Clone into a temporary folder outside the project. Read its
   README, `install.py` and `upstream.py`. Run
   `python3 install.py install --project <absolute-project-root> --refresh-imports --dry-run`.
   Review the upstream commits, file list and collisions.
4. **Apply.** If the dry run is clean, run it without `--dry-run`. The installer
   fetches upstream even when the jstack version is unchanged. Run
   `install.py check` and the doctor skill, then inspect the target diff.
5. **Conflicts.** A modified managed file or an unmanaged collision needs a
   scoped resolution that keeps the user's edits. There is no force flag.

The installer refreshes the imported grilling skills and any Claude SEO
installation made with `setup-seo.py`. Impeccable and separately installed SEO
skills use their own update workflows. Preserve project config, hooks, runtime
setup and other skills. Commit, push or deploy only if asked. Agents may need a
reload to discover updated skills.
