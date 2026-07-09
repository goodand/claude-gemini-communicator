# Troubleshooting

## Image Evidence And Text Judgment Drift Apart

Problem:
- image evidence is shown in one place
- text judgment is written elsewhere
- later readers cannot tell which judgment belongs to which evidence

Fix:
- bind both to the same `item_id`
- keep `image_evidence` and `text_judgment` as separate manifest fields
- derive markdown cards from that manifest instead of hand-writing free-form summaries

## Comparison Outcome And Policy Decision Collapse Into One Field

Problem:
- the comparison winner is treated as if it were already the active policy choice

Fix:
- keep `comparison_outcome` and `policy_decision` separate
- keep `qualitative_winner_candidate` and `recommended_current_default` separate
- require an explicit promotion gate before default replacement

## Human Reading Order And Machine Schema Order Diverge

Problem:
- markdown is optimized for reading
- machine consumers need stable field order and explicit keys

Fix:
- keep the manifest canonical
- keep markdown as a derived review surface
- never reopen markdown as the only truth source

## Ambiguous Multimodal State Hidden Without Explicit Pending Marker

Problem:
- image evidence exists
- text judgment exists
- but semantic closure is still unresolved
- the artifact reads as if it were final

Fix:
- emit `review_state=pending`
- list `pending_reasons`
- do not imply semantic closure or final promotion until the pending state is cleared
