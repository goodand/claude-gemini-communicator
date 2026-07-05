# Runtime Paths

## Core user-visible paths

1. `home -> delete -> report`
2. `home -> precious -> result -> home`
3. `home first render -> carousel visible`

## Typical files

- `main.js`
- `src/components/HomeManager.js`
- `src/components/ReportManager.js`
- `src/services/PhotoService.js`
- `src/plugins/RecocolPhotos.ts`

## Repo-specific questions

- Does the change keep `launch_to_carousel_ms` instrumentation alive?
- Does `delete` still update the next visible card predictably?
- Does `recorded` still trigger same-day refresh or suppression?
- Is any UI transition now dependent on an unverified async side effect?

## Verdict hints

- `merge-now`: runtime path is coherent and already has runtime proof
- `merge-after-runtime-proof`: code is coherent but proof is still missing
- `split-before-merge`: good runtime changes are buried with noise
