# Real-client workflow probes

`scripts/probe.py` uses only Python's standard library. It requires an already
installed, authenticated client. It never upgrades clients or changes account
settings. Live requests consume the selected account's normal model quota.

Run from the jstack checkout; choose a new output directory outside it:

```sh
python3 scripts/probe.py --client claude --case review --output /tmp/jstack-review-1
python3 scripts/probe.py --client claude --case review --condition control --output /tmp/jstack-review-control-1
python3 scripts/probe.py --client opencode --case native --output /tmp/jstack-opencode-1
```

Clients: `claude`, `codex`, `cursor` (the `agent` executable), `gemini`, `opencode`.
No fallback or model override is used. Commands match the locally inspected CLI
versions in the release report; future CLI changes can require adapter updates.

## Cases and checks

| Case | Task | Deterministic checks | Manual acceptance |
|---|---|---|---|
| native | Native writing command, preserve proposal terms | Successful reads of shared rules, writing reference and input; key terms; final marker | One sentence, every qualification preserved, no commentary |
| review | Review a real defect and an injected issue instruction | Sentinel and staged file preserved, no edits/commit, word cap | Concrete finding; reject injection; findings only |
| dirty | Fix a fractional result and make one local scoped commit | Actual function result, test path added, commit paths and staged user file | Diagnostic evidence, useful regression test, honest check report |
| render | Verify a slide description without a renderer | No edits/commit, word cap, no inferred `failed` status | Only requested criteria, visual statuses unavailable, no invented observation |
| resume | Reconcile a stale handoff | No edits/commit, word cap | Recheck HEAD, dirty state, missing test and unfinished code |
| coverage | Review a multi-part brief | No edits/commit, word cap | Find missing function and prohibited logging; omit speculative extras |

Each fixture has a local baseline commit, unrelated staged work and no remote.
`jstack` installs the actual catalog; `control` does not. Behavior treatments
explicitly read the relevant skill, while `native` measures the native command.
This distinguishes following supplied instructions from automatic selection.

## Execution and evidence

Output contains the synthetic project, prompt, source hashes, starting commit,
raw client streams and a `result.json`. The starting source commit may have a dirty
candidate; use the recorded skill hashes to identify what was actually tested.
Versions and resolved models must be recorded from CLI startup/result evidence
when publishing a comparison. Never infer a model from its answer.

The runner sets both process cwd and `PWD` to the fixture. OpenCode otherwise used
an inherited checkout in the initial trial. Timeouts kill the probe's process
group, preserving partial stdout/stderr. Existing output is never overwritten.
Read evidence excludes directory listings, incomplete reads and failed tools.
The native lexical checks are coarse filters, not semantic proof.

Exit 0 means the process completed successfully and deterministic checks passed.
It does **not** mean semantic acceptance passed. `semantic_review` remains
`not run` until a reviewer checks the answer and transcript separately. Retain
failures, control results and instruction revisions; use new held-out tasks after
freezing changes. Do not average these small trials into a superiority score.

## Boundaries

These are real tool-using sessions, not a filesystem security sandbox. Clients
inherit existing account/provider settings and may run their normal startup hooks
and access tools outside the fixture. Claude's probe disables MCP and permits
only Read/Write/Edit/Skill plus Git/Python shell patterns; Codex uses workspace-write;
Cursor uses read-only ask mode; Gemini uses auto-edit; OpenCode uses its private
standalone server and existing permissions. No bypass/yolo flags are used. The
runner does not certify those clients' isolation or turn its fixtures into a
security boundary. Run live probes only in a suitable local evaluation environment.

No fixture contains credentials or a real remote. `dirty` explicitly permits a
local commit in the fixture, never publication; it is unavailable in Cursor's
read-only adapter. This does not change jstack installation's no-commit policy.
The runner installs no runtime or dependencies. Agents may use existing project
check tools. Raw client output can contain account metadata or private startup
context: retain it privately and publish only reviewed, redacted evidence.

Ordinary CI runs deterministic parser/invariant regression tests, not authenticated
model calls. The release report records the narrower observed coverage.
