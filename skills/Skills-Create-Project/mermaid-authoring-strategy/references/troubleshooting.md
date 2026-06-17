# Mermaid Troubleshooting

렌더 실패 시 구문 디버깅 우선 접근법.

## Golden Rule

**렌더 실패 = 구문 문제 먼저, 스타일 문제 나중.**

## CASE-001: Syntax error in text

증상: Mermaid가 `Syntax error in text` 또는 `Parse error` 출력.

원인 우선순위:
1. 노드 ID에 공백 또는 특수문자 (`/`, `(`, `)` 등)
2. 라벨에 이스케이프 안 된 특수문자
3. `subgraph` 블록 미닫힘 (`end` 누락)
4. `classDef`/`linkStyle`의 인덱스 오류
5. 엣지 라벨 안에 줄바꿈 또는 따옴표

복구 절차:
1. 모든 라벨, classDef, linkStyle, subgraph를 제거
2. 노드 ID와 `-->` 만 남긴 최소 그래프로 축소
3. 렌더 확인
4. 제거한 요소를 하나씩 복원하며 실패 지점 특정

## CASE-002: subgraph 관련 파싱 실패

증상: subgraph를 추가하면 그래프 전체가 렌더 실패.

흔한 원인:
- `end` 키워드 누락
- subgraph ID에 공백 사용 (`subgraph My Group` → `subgraph MG[My Group]` 형태로)
- 같은 노드를 두 개 이상의 subgraph에 중복 배치

복구: subgraph 없이 먼저 렌더 확인 → subgraph를 하나씩 추가.

## CASE-003: 엣지 라벨이 파싱을 깨뜨리는 경우

증상: `-->|label|` 형태에서 파싱 실패.

흔한 원인:
- 라벨 안에 `|` 문자 포함
- 라벨 안에 괄호 `()`, `[]` 포함
- 라벨이 너무 긴 경우 (줄바꿈 삽입 시도 시)

안전한 패턴: `A -->|short label| B` (영문 기준 20자 이하 권장)

## CASE-004: classDef / linkStyle 인덱스 오류

증상: 스타일을 추가하면 렌더 실패 또는 무시됨.

원인:
- `linkStyle` 인덱스는 엣지 선언 순서에 의존 — 엣지를 추가/삭제하면 인덱스가 밀림
- `classDef` 이름에 하이픈 사용 시 일부 버전에서 파싱 문제

권장: 스타일은 구조 확정 후 마지막에 추가. 엣지 수가 바뀌면 linkStyle 재계산.

## CASE-005: Mermaid 버전 불일치

증상: 로컬에서는 렌더되지만 다른 환경에서 실패.

원인: Mermaid 버전 차이 (특히 10.x vs 11.x 구문 차이).

대응:
- `@11` CDN 고정 (`https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs`)
- `securityLevel: "loose"` 사용 시 주의 (환경별 기본값 다름)

## 디버깅 체크리스트

1. [ ] 노드 ID가 영문+숫자만 사용하는가?
2. [ ] 모든 `subgraph`에 `end`가 있는가?
3. [ ] 라벨에 이스케이프 필요한 특수문자가 없는가?
4. [ ] `-->` 만 쓴 최소 그래프가 렌더되는가?
5. [ ] 스타일을 제거해도 같은 에러가 나는가?
