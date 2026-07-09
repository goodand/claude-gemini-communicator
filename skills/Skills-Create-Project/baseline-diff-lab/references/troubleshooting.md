# Troubleshooting — baseline-diff-lab

## CASE-001: post-fix만 있고 pre-fix가 없음

**증상**: 개선 보고는 있는데 기준선이 없다.
**원인**: smoke 뒤에 바로 수정해서 pre-fix artifact를 저장하지 않았다.
**해결**: 수정 전에 pre-fix baseline을 먼저 저장한다.
**교훈**: diff lab은 항상 pre-fix artifact로 시작한다.

## CASE-002: planner와 compute를 동시에 돌려 plan JSON이 불안정함

**증상**: `compute`가 plan JSON decode 오류를 낸다.
**원인**: 같은 plan 파일을 planner가 쓰는 동안 compute가 동시에 읽었다.
**해결**: planner 완료 후 compute를 순차 실행한다.
**교훈**: `metricize -> planner -> compute`는 순서형 handoff다.
