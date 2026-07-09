# python-static-diagnostic-fixer Troubleshooting

## Cases

### CASE-001: runtime 정상 + unused module constant

- 대상: `edge-case-generator/scripts/edgegen.py`
- 증상:
  - `py_compile`은 통과
  - static audit에서 `RULE_TYPES`가 `unused_variable`로 1건 검출
- 처리:
  - 기능과 무관한 미사용 상수만 제거
  - 로직 재구성 없이 최소 수정으로 종료
- 결과:
  - post-fix audit finding `1 -> 0`
  - `edge-case-generator` 테스트와 `py_compile` 모두 유지
