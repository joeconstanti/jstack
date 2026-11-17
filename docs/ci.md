# Continuous integration

`Check jstack` validates every pull request and every push to `main`. Topic
branch pushes use the pull-request run, avoiding duplicate validation.
Open a PR to validate a topic branch. Every PR, including documentation changes,
runs catalog validation and the complete unittest suite on Ubuntu with Python
3.11, 3.13 and 3.14. Do not add path filters that leave required checks pending.

New commits to a PR cancel superseded runs for that PR only. Default-branch
pushes use distinct commit groups so each merged commit retains its own result.
Cancellation is not acceptance; the latest PR head must pass all three jobs.

## Why these gates remain

Catalog validation is the fast first gate: reject invalid skill metadata,
references and invocation policies before integration tests. The complete
unittest suite verifies project-only installation, collision/ownership boundaries,
rollback, provider adapters and deterministic probe parsing. Python 3.11 covers
the advertised minimum; 3.13 and 3.14 retain the requested newer-runtime
compatibility checks against standard-library changes.

There is one workflow, no dependency installation, app build, packaging or live
model suite. The corrected PR scope is one run with three jobs, down from two
runs with six jobs each (75% fewer job submissions per PR head). Main pushes keep
three jobs, down from six. No assertion or substantive validation stage is removed.

Required commands:

```sh
python3 install.py validate
python3 -m unittest discover -s tests -v
```

For workflow edits, also run `actionlint .github/workflows/check.yml` when installed.
No third-party Python packages or authenticated clients are needed for CI.
SEO tests use disposable offline fixtures; live client probes remain opt-in and
are not part of this matrix. CI does not deploy, install project runtimes or
certify native agent discovery/rendered behavior.

## Platform scope

The installer and diagnostics use standard-library Python and Git. There is no
native macOS app build, macOS-only test, platform conditional or platform skip in
the test suite. Symlink confinement, executable modes, rollback, metadata and
provider discovery fixtures run unchanged on Ubuntu. Hosted macOS is therefore
not a required gate for this generic validation.

Ubuntu does not establish macOS filesystem behavior, including case folding and
filesystem-specific symlink/permission differences. When changing path handling,
optionally run the same two commands on a local Mac and record the OS/Python and
result separately. These checks are useful additional platform evidence, not a
native-app or provider-discovery certification. No optional hosted workflow is
needed for the current codebase.

## Runner failures and local capacity

On 17 November 2026, run `44131106158` passed five jobs but its macOS/Python 3.13
job was cancelled before any steps ran. Its annotation was "The job was not
acquired by Runner of type hosted even after multiple attempts", with arm64
capacity notices. Intel macOS replacements also remained queued. Those historical
runs are non-passing and superseded by the explicitly authorized Ubuntu-only
workflow; they are not test failures or evidence of current acceptance.

Inspect exact-head job steps and annotations before retrying. Fix reproducible
failures rather than repeatedly rerunning an unchanged queue failure. During
coordinated campaigns, honor the shared heavy-local-verification slot; use focused
checks and hosted CI while waiting. Do not suppress failures or weaken assertions.
