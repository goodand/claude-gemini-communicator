# Troubleshooting

## One-Shot Caption Is Treated As Final Understanding

Problem:
- the first caption or first text judgment is treated as closed understanding

Fix:
- keep the first text as a hypothesis
- reinject image evidence with that hypothesis
- require at least one explicit refinement decision before closure

## Baseline Anchor Drifts Into The Latest Winner

Problem:
- the most recent better-looking result silently becomes the new comparison baseline

Fix:
- keep `baseline_anchor` explicit
- record `delta_from_baseline` separately
- require a later promotion gate before replacing the current default

## Reinjection Context Is Lost Between Passes

Problem:
- later passes cannot explain why the model looked again or what changed

Fix:
- keep `pass_index`
- keep `next_refinement_focus`
- preserve the bounded context used for each new pass in the loop manifest

## Pending State Is Hidden Behind Apparent Fluency

Problem:
- image evidence and text judgment both exist
- the artifact sounds confident
- but semantic closure is still unresolved

Fix:
- emit `review_state=pending`
- list `pending_reasons`
- do not derive final review artifacts as if closure were complete
