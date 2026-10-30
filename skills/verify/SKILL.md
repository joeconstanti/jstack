---
name: verify
description: "Prove scoped web changes in a real browser: rendered routes, mobile and desktop layouts, key interactions and console errors. Use for /verify or browser acceptance checks."
---

# verify

Read `.agents/jstack/rules.md` first and apply it. The goal is rung 4 (observed), or a clear reason why it was not reached.

1. **Target.** Use the preview skill to find this checkout's app. List the
   routes that the change touches, plus shared navigation, header and footer.
   Use the project's browser QA scripts when they exist.
2. **Baseline.** For a bug fix, reproduce the failure on the same route and
   viewport first, then watch the same path pass after the fix. For a visual
   change, capture main, the live site or a supplied reference. When the user
   asks for a match, compare by image diff and keep the reference unchanged.
3. **Drive the real user path** at desktop and narrow mobile widths. Let fonts,
   images and animations settle. Check the main action, keyboard focus,
   relevant loading, empty and error states, internal links, and console and
   network failures. Capture the action and the resulting state, not only the
   final screen. Check side effects that matter: form payload, tracking event,
   redirect.
4. **Stay safe.** Do not submit real leads, send messages, buy or change account
   data. Use a test path that the project provides.
5. **Record** the URL, viewport, scenario and result of each check. Save
   evidence under `.agents/jstack/reports/verify/` or where the user asks. Stop
   only processes you started, and keep the evidence.

Report passes, failures and gaps. A tracking request is not account
attribution. Fix only when implementation is authorized.
