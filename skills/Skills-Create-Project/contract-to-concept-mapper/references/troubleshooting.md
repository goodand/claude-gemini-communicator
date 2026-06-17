# Troubleshooting — contract-to-concept-mapper

## CASE-001: 요약은 있는데 traceability가 없음

- **증상**: 상위 개념 설명은 생성됐지만, 어떤 checklist/schema/task 조각에서 나왔는지 추적 불가
- **원인**: contract unit 계층 없이 바로 자연어 summary를 만들었음
- **해결법**: `contract unit -> concept unit -> rendered summary` 3단계를 유지
- **교훈**: 이 skill의 핵심은 요약보다도 `lift 근거`를 남기는 것이다

## CASE-002: 개념 lifting이 과도해서 boundary가 흐려짐

- **증상**: checklist/task를 읽고 나온 concept summary가 너무 넓어서 실제 경계가 흐려짐
- **원인**: contract unit을 바로 상위 개념 하나로 뭉쳤고 relation/boundary를 먼저 정리하지 않았음
- **해결법**: render 전에 `boundary description`, `semantic relation map`을 먼저 만든다
- **교훈**: mapping이 안 되는 문제는 artifact 체인보다도 `boundary 없는 lifting`에서 자주 생긴다

## CASE-003: project context 부족 상태에서 무리하게 개념을 복원함

- **증상**: concept summary는 생성되지만 weak support가 많고 사용자 의도와 어긋남
- **원인**: 입력 contract는 충분하지 않은데 project context 부족을 표시하지 않았음
- **해결법**: uncertainty/weak support를 명시하고 과도한 복원을 멈춘다
- **교훈**: 이 skill은 concept을 “반드시” 복원하는 도구가 아니라, 근거 있는 범위 안에서만 lift해야 한다
