# Cohort Expansion Truth Sync

Use this reference when a late-arriving image has already closed all required arms and must be folded into an existing canonical cohort without restarting the whole experiment.

## Goal

Keep producer truth, consumer truth, closure docs, and registry surfaces aligned after the cohort grows.

## When To Use

- a new image has a stable per-image bundle
- the current small-batch or corpus-ready cohort was already published
- downstream consumers should see the widened cohort as canonical truth

## Required Truth Order

1. Per-image bundle must exist under workspace-owned canonical paths.
2. Aggregate bundle must be regenerated from the current included image set.
3. Consumer auto-eval or downstream bundle must be regenerated from the same image set.
4. Closure report, master plan, and registries must be patched to the same cohort size and image list.

## Minimal Sync Checklist

1. Verify the new image is truly included by evidence-only gates.
2. Regenerate the aggregate bundle with the existing builder.
3. Regenerate the consumer artifact from canonical inputs.
4. Read back the written files from disk, not just stdout.
5. Patch closure/master-plan language to the new image count.
6. Patch artifact index and session registry with any missing image-specific paths.

## Common Drift To Catch

- aggregate bundle still references the old image set
- consumer auto-eval still reads stale bundle paths
- closure report still states the previous cohort size
- registry omits the newly added image-specific artifacts

## Do Not

- create a second aggregate schema at the same canonical path
- trust runner stdout without checking the on-disk manifest
- change default baseline policy just because the cohort widened

## Current Proven Pattern

- `phase1` stable cohort widened after `image8.png` reached bounded `4-mode` closure
- producer, consumer, closure, master plan, and registries all required follow-up sync
