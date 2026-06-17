# Troubleshooting — agent-graph-ir

## CASE-001: Pydantic만 설치된 환경

**증상**: `jsonschema`, `graphviz`, `pydot`, `langfuse` import가 실패한다.
**원인**: 현재 workspace Python 환경에 optional dependency가 없다.
**해결**: first slice는 `pydantic`만 필수로 쓰고, 나머지는 optional adapter 또는 파생 text 출력으로 분리했다.
**교훈**: skill first slice는 dependency-light하게 만들어야 바로 실행 검증이 가능하다.

## CASE-002: OpenAI screenshot skill stdout이 여러 줄인 경우

**증상**: app/window capture나 multi-display capture에서 screenshot helper가 파일 경로를 여러 줄로 출력한다.
**원인**: OpenAI curated `screenshot` skill은 match된 window/display마다 한 줄씩 path를 출력한다.
**해결**: `emit-observe-events-from-screenshot-output`로 stdout text file을 받아 multi-event payload로 변환한다.
**교훈**: screenshot bridge는 단일 artifact 가정이 아니라 path-list contract를 기본으로 가져가야 한다.

## CASE-003: screenshot helper 실행은 성공했는데 IR event가 비어 있는 경우

**증상**: subprocess는 성공 코드로 끝났는데 생성된 observe event가 없다.
**원인**: helper stdout에 실제 screenshot path가 없거나, path가 stdout 대신 stderr로만 출력되었다.
**해결**: `run-screenshot-bridge`는 stdout path가 하나도 없으면 즉시 실패하게 두고, helper가 경로를 stdout에 한 줄씩 출력하도록 맞춘다.
**교훈**: bridge 단계에서는 “이미지 생성 성공”보다 “stdout contract 준수”를 먼저 확인해야 한다.
