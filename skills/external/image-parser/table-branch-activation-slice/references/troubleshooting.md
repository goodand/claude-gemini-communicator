# Troubleshooting

Use this skill in fail-closed mode. If selection provenance is unclear, boot verification is incomplete, parser output cannot be normalized, or the wrapper starts to outrun the evidence, stop the slice and keep the branch inactive.

## CASE-001: Automatic selection promoted the wrong table surface

**Symptom**:
- the parser smoke runs on a crop that is mechanically valid but semantically unrelated to the intended table
- the full image still contains the table context, but the selected crop produces weak or nonsensical structure
- `selected_surface_path` or the triage rationale is missing from the selection manifest

**Cause**:
- Step 0 was skipped, weakened, or treated as automatic component fanout
- a crop was promoted without explicit reviewed triage acceptance

**Resolution**:
- stop before widening Step 2
- rerun the triage gate and force one explicit decision:
  - `use_full_image`
  - `use_reviewed_crop`
  - `not_a_table_candidate`
  - `needs_manual_audit`
- prefer the full image unless triage explicitly approves a reviewed crop

**Safe fallback**:
- exclude the image from the parser smoke set and keep the branch inactive until a trusted surface exists

**Lesson**:
- do not let automatic crop selection activate the table branch

## CASE-002: The parser looks installed, but Step 1 is not really complete

**Symptom**:
- the launcher exists, but boot smoke hangs, emits non-machine-readable startup noise, or falls back to home-scoped cache paths
- local `PP-StructureV3` mode is not clearly selected
- the backend is being described as active even though no bounded boot smoke artifact exists

**Cause**:
- installation or registration was treated as equivalent to runtime verification
- launcher hardening for cache path and local mode was left implicit instead of proven by smoke

**Resolution**:
- keep the branch at inactive status
- run the bounded full boot smoke first and confirm:
  - launcher starts cleanly
  - local `PP-StructureV3` mode is selected
  - one real command completes without indefinite wait
- do not mark the backend as activation-ready until the smoke artifact exists

**Safe fallback**:
- stop after Step 0 and continue using existing OCR or triage evidence only; do not enter real-image parser smoke yet

**Lesson**:
- Step 1 is a runtime proof gate, not a paperwork gate

## CASE-003: Real-image parse looks hung, but it is actually a long-latency bounded run

**Symptom**:
- the first real parse on a PPT-derived image is quiet for a long time
- there is little stdout movement, so the run looks dead even though the process is still doing work
- operators are tempted to kill the parse and retry repeatedly

**Cause**:
- real `PP-StructureV3` parsing can stay high-latency even with warm local assets
- silence on stdout is being mistaken for proof of deadlock

**Resolution**:
- keep the smoke narrow at `1` to `2` triage-approved images
- judge the run by bounded artifact production and end-to-end completion, not stdout chatter alone
- only classify the run as failed after the bounded smoke window ends with no raw output or report artifact

**Safe fallback**:
- if the bounded window expires without real output, stop at Step 1 status and keep the branch as boot-verified but not parser-proven

**Lesson**:
- long latency is not the same as successful activation, but it is also not proof of failure

## CASE-004: Raw parser output exists, but canonical normalization is not defensible

**Symptom**:
- the parser emits a table-like response, but rows or cells cannot be mapped cleanly into `Table -> Row -> Cell`
- required canonical fields are missing, unstable, or cannot be traced back to the source image and raw output
- normalization would require guessed rows, guessed spans, or invented provenance

**Cause**:
- the raw output is not stable enough yet for canonical promotion
- manifest-shape or provenance recovery drift hides the data needed for traceable normalization

**Resolution**:
- stop at Step 3
- inspect the smallest bounded raw output and provenance manifest that failed
- rerun only the affected image if the problem is manifest drift or a malformed raw artifact
- do not fabricate canonical rows, cells, spans, or confidence values

**Safe fallback**:
- keep the backend as a candidate parser with raw evidence only; do not expose it as the active table branch

**Lesson**:
- normalization is a proof gate, not a best-effort formatting pass

## CASE-005: Wrapper work outran normalization or reads the wrong source

**Symptom**:
- `get_tables`, `get_table_rows`, or `get_cells` is wired directly to raw parser output
- a consumer smoke exists, but it proves only a custom raw adapter rather than the normalized contract
- wrapper implementation starts before Step 3 is stable

**Cause**:
- Step 4 was treated as a convenience task instead of a post-normalization gate
- downstream urgency pulled the wrapper ahead of canonical schema proof

**Resolution**:
- stop wrapper promotion immediately
- re-anchor the wrapper to normalized records only
- rerun the bounded consumer smoke against the normalized artifact, not the raw parser response

**Safe fallback**:
- keep the wrapper out of the active path and continue consuming the normalized JSON directly until the read-only surface is contract-correct

**Lesson**:
- the wrapper proves branch usability only when it reads the canonical normalized layer

## CASE-006: The parser works mechanically, but the branch still should not be promoted

**Symptom**:
- Step 2 technically succeeds, but the detected table region, row recovery, or cell structure is not materially better than the current OCR-only fallback
- the branch is tempting to promote because the tool "worked"

**Cause**:
- mechanical smoke success was confused with pipeline-valid improvement
- the slice did not answer whether the parser actually improves the target workflow

**Resolution**:
- compare the bounded parser result against the current OCR-backed baseline before any promotion claim
- if the parser does not improve structure recovery enough to justify normalization and wrapper use, hold promotion
- document the limitation in the bounded report instead of stretching the evidence

**Safe fallback**:
- keep using the existing OCR-first path for the current task and leave the parser branch in candidate status

**Lesson**:
- active branch status requires workflow improvement, not just a runnable backend
