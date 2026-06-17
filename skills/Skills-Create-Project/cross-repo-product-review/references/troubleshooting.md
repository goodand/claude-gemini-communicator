# Troubleshooting — cross-repo-product-review

## CASE-001: Product intent drift invalidated early findings

**증상**: surface repo를 generic editor로 읽어 downstream conclusions가 틀어졌다.
**원인**: review 시작 전 product purpose를 잠그지 않았다.
**해결**: intent lock을 workflow step 1로 강제했다.
**교훈**: product review는 코드보다 먼저 product boundary를 고정해야 한다.

## CASE-002: Codex fixed named lines but missed sibling structural fields

**증상**: 지적된 항목은 수정됐지만 같은 구조의 인접 필드가 남아 residual issue가 재발했다.
**원인**: patch verification이 named finding closure에만 머물렀다.
**해결**: structural-class completeness guardrail을 추가했다.
**교훈**: closure review는 diff가 아니라 구조 단위로 확인해야 한다.
