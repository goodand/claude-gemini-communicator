# Troubleshooting — agent-tool-benchmark

## CASE-001: AgentBench metric 미구현 경고

- 증상: SKILL.md에 "9개 벤치마크"로 기재되어 있지만 registry에는 8개 벤치마크만 대응
- 원인: AgentBench는 8개 환경별 normalized score를 사용하여 하나의 범용 수식으로 표현 불가
- 해결: 문구를 "8개 벤치마크, 9개 메트릭"으로 정정, AgentBench는 조사만 수행으로 명시
- 교훈: 조사 대상과 구현 대상의 수를 분리 표기해야 한다

## CASE-002: GED 근사와 정확 GED의 차이

- 증상: `graph_edit_distance_score()`가 정확한 GED가 아님
- 원인: 정확한 GED는 NP-hard, v0에서는 symmetric difference로 근사
- 해결: KB의 simplification boundary에 명시, 정확 GED가 필요해지는 조건 기록
- 교훈: 간소화는 허용하되 경계 조건을 문서화해야 한다
