# KB Checklist Pipeline Family: implementation_output

## Scope

- 최종 산출물이 `script` 또는 `md/txt/image`가 아닌 비문서 구현물일 때 사용하는 branch
- 이 branch는 후속 자료를 점진적으로 더 읽어야 한다

## Progressive Read Chain

1. branch index
2. canonical KB
3. consistency checklist
4. implementation checklist
5. `scripts/pipeline_router.py` 결과 확인
6. TDD 파일 생성
7. 구현 파일 생성
8. smoke/evidence 작성
9. raw smoke artifact 보존
10. evidence ledger / support audit 정리
11. drift/debug 정리
12. raw smoke report면 metric artifact로 정규화
13. before/after diff 작성
14. 필요하면 [baseline-diff-bridge-at2026-03-16-23-17.md](./baseline-diff-bridge-at2026-03-16-23-17.md)로 handoff
15. router payload field는 [router-output-contract-at2026-03-18-23-32.md](./router-output-contract-at2026-03-18-23-32.md)로 고정

## TDD Rule

- script를 만들면 `scripts/test_<name>.py`를 같이 만든다
- script가 아니어도 `md/txt/image`가 아닌 구현물은 TDD 또는 검증 파일을 먼저 만든다
- 구현은 TDD 계약이 나온 뒤에만 시작한다

## Follow-up Evidence

- smoke 결과
- troubleshooting case
- evidence ledger / support audit
- debug 메모
- raw smoke report를 diff 단계로 넘길 때는 metric artifact
- before/after diff가 있으면 report로 남긴다
- 전체 규칙은 [Execution Contract To Evidence Pattern](../../../skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md) 참고
