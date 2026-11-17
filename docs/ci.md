# Continuous integration

`Check jstack` validates every pull request and every push to `main`. Topic
branch pushes use the pull-request run, avoiding a duplicate six-job matrix.
Open a PR to validate a topic branch. All PRs, including documentation changes,
keep catalog validation and the full test matrix: Linux/macOS with Python
3.11, 3.13 and 3.14. macOS uses the supported `macos-15-intel` image because
GitHub reported arm64 runner acquisition failures; this retains macOS filesystem
and symlink coverage but does not claim hosted Apple Silicon coverage. See the
[official runner labels](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
Do not add path filters that leave required checks pending.

New commits to a PR cancel superseded runs for that PR only. Default-branch
pushes use distinct commit groups so each merged commit retains its own result.
Cancellation is not acceptance; the latest PR head must pass every matrix job.

Run the same commands locally before publishing when local capacity is available:

```sh
python3 install.py validate
python3 -m unittest discover -s tests -v
```

For workflow edits, also run `actionlint .github/workflows/check.yml` when installed.
No third-party Python packages or authenticated clients are needed for CI.
SEO tests use disposable offline fixtures; live client probes remain opt-in and
are not part of this matrix. CI does not deploy, install project runtimes or
certify native agent discovery/rendered behavior.

Hosted macOS jobs can remain queued without executing a step. Inspect the job
steps and annotations before calling this a test failure. A cancelled or failed
run remains non-passing; wait for the current head's complete matrix rather than
merging on a partial result or repeatedly rerunning an unchanged queue failure.
On 17 November 2026, run `44131106158` passed five jobs but its macOS/Python 3.13
job was cancelled before any steps ran; the run was marked failed. Its failure
annotation was "The job was not acquired by Runner of type hosted even after
multiple attempts", with macOS arm64 capacity notices. This is
historical runner/cancellation evidence, not a passing six-job result.

During coordinated campaigns, honor the shared heavy-local-verification slot;
use focused checks and hosted CI while waiting. Retain actual failures, fix
reproducible causes and rerun affected checks only after a relevant change.
