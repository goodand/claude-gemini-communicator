# Workflow

## 1. Pick the right execution lane

Use this order:
1. Xcode runtime + app logs
2. Instruments for deeper native timing
3. `idb` for simulator interaction automation
4. Chrome DevTools only if WebView-side JS needs a second breakdown
5. OpenTelemetry only if backend spans are on the launch path

## 2. Branch and worktree discipline

Prefer a new experiment worktree when:
- the current branch is dirty
- the experiment changes launch-path code
- you need repeatable before/after measurements

Recommended pattern:
- stable base branch
- one experiment branch per hypothesis
- one worktree per experiment branch

## 3. Minimal instrumentation rule

Instrument only the launch critical path first:
- native fetch
- JS ranking or filtering
- thumbnail roundtrip
- geocode or other network detail calls
- paint finalize

Do not add unrelated probes until the current bottleneck is clear.

## 4. Simulator automation rule

If permission popups block reproducibility:
- use `idb screenshot`
- use `idb ui describe-all`
- find the visible button from AX tree
- tap it with `idb ui tap`

Do not rely on manual approval if the experiment needs repeated runs.

## 5. Run-count rule

Default is 5 runs.

Use fewer only when:
- the user explicitly asks for a quick smoke run
- the build is still unstable and you are only validating instrumentation

## 6. Commit rule

Safe to commit:
- instrumentation code
- reusable automation scripts
- derived analysis scripts
- stable result notes if the user wants them tracked

Usually keep local only:
- Podfile path rewrites created by worktree hacks
- Podfile.lock churn from local install hacks
- `node_modules` symlinks
- raw screenshots, temporary dumps, or temporary run folders

## 7. Result note rule

Use minute-stamped filenames:
- `YYYY-MM-DD-HH-MM_description.md`

Include:
- exact branch
- exact worktree path
- exact commands used
- sample size
- pass/fail against KPI
- next recommended experiment
