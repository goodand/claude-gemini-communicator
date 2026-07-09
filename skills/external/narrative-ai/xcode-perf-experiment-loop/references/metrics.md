# Metrics

## Core launch KPI

Primary KPI:

- `launch_to_carousel_ms`

Default target:

- `p95 <= 2000 ms`

## Percentile rule

For small `n`, use nearest-rank percentiles.

Given sorted ascending values `x_(1) <= ... <= x_(n)`:

- `p50 = x_(ceil(0.50 n))`
- `p95 = x_(ceil(0.95 n))`
- `max = x_(n)`

With 5 runs, `p95` is the largest observed value.

## Cumulative delay

Cumulative delay means multiple serial spans add directly to total launch time.

Example approximation:

`launch_to_carousel_ms ~= native_fetch_ms + current_photo_detail_ms + paint_finalize_ms`

Interpretation:
- if these spans together explain most of launch time, launch is serially accumulated
- if one span shrinks and launch shrinks by about the same amount, that span is on the critical path

## Amplified delay

Amplified delay means one slow dependency blocks a larger combined stage.

Common pattern in this repo:

`current_photo_detail_ms = max(current_thumbnail_roundtrip_ms, current_geocode_ms)`

If:
- `current_photo_detail_ms ~= current_geocode_ms`
- `current_geocode_cache_hit=false`
- `launch_path_network_calls > 0`

then geocode is amplifying launch delay by locking the whole detail stage.

## Heuristic findings

### Geocode-dominant launch path

Strong signal when all are true:
- `current_geocode_ms` is the largest repeated span
- `current_photo_detail_ms ~= current_geocode_ms`
- launch path network calls stay above zero

### Thumbnail-dominant launch path

Signal when:
- `current_thumbnail_roundtrip_ms` is the largest repeated span
- `current_photo_detail_ms ~= current_thumbnail_roundtrip_ms`
- geocode is cached or deferred

### Native fetch-dominant launch path

Signal when:
- `native_fetch_ms` remains largest after warm runs
- p50 and p95 both track native fetch changes closely

## Report language

Always separate:
- observed metrics
- inference from metrics
- recommendation

Example:
- Observed: `current_geocode_ms` averaged 615 ms across 5 runs
- Inference: geocode dominated the current-photo detail stage
- Recommendation: remove geocode from launch path or defer it behind first paint
