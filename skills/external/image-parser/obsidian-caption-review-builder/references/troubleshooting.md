# Troubleshooting

## No ledger files matched

Symptom:

- the script exits with `No ledger files matched.`

Check:

- the glob is bounded to the intended run
- smoke ledgers are excluded by default
- the command is being run from the repo root if you are using relative globs

Fix:

- tighten or correct `--ledger-glob`
- add explicit `--exclude-glob` rules only if you intend to override the default smoke exclusion

## Images do not render in Obsidian

Symptom:

- markdown is generated, but embeds do not resolve in Obsidian

Check:

- which mode was used
- whether the images are inside the vault or reachable through the expected relative path

Fix:

- prefer `--mode canonical-copy`
- use `--mode direct` only when the source image layout is stable relative to the output markdown
- use `--mode prefixed` only when the vault already exposes the prefixed asset path

## Wrong prefixed path setup

Symptom:

- prefixed embeds are present but broken
- or the run fails after switching to prefixed mode

Check:

- `--mode prefixed` requires both `--source-root` and `--embed-prefix`
- every completed image path must be under `--source-root`

Fix:

- correct `--source-root`
- keep the prefix aligned with the actual vault mount or symlink path

## Duplicate filenames in copied assets

Symptom:

- copied review assets contain multiple similarly named files

Why:

- the same filename can occur across multiple datasets or ledgers

Fix:

- this is expected
- the builder adds an `image_id_` prefix only when needed to avoid collisions

## Non-completed records have no image embed

Symptom:

- a record appears in the review without an embedded image

Why:

- only `completed` records with an existing image file receive embeds

Fix:

- inspect the `status` field
- treat missing embeds on non-completed records as a review signal, not as a rendering bug

## Canonical output location drift

Symptom:

- the review is being written under `control/user_decisions/` as if it were already a decision record

Fix:

- keep the full review surface under `control/project_domain/resources/reports/`
- promote only explicit human decisions into `control/user_decisions/`
