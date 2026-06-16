# Mermaid Parser-Safe Subset

Mermaid 11.13.0에서 안정적으로 렌더되는 구문 부분집합 정의.

## Safe Baseline (항상 안전)

```
graph TD
    A --> B
    A --> C
    B --> D
```

- 노드 ID: 영문 대소문자 + 숫자 (2~4자 권장)
- 엣지: `-->` (실선 화살표)
- 방향: `TD`, `LR`

## Safe + Labels

```
graph TD
    A[Short Label] --> B[Another]
    A -->|feeds| C[Third]
```

- 노드 라벨: `[]` 안에 20자 이하 영문
- 엣지 라벨: `|label|` 안에 15자 이하 영문
- 한국어 라벨도 가능하지만 짧게 유지

## Safe + Subgraph

```
graph TD
    subgraph SG1[Group Name]
        A[Node A]
        B[Node B]
    end
    A --> C
```

- subgraph ID: 영문 대소문자 + 숫자
- subgraph 라벨: `[]` 안에 짧은 이름
- 반드시 `end`로 닫기
- 한 노드는 하나의 subgraph에만 소속

## Incrementally Safe (구조 안정 후 추가)

### 다양한 엣지 타입

```
A --> B       %% 실선 화살표
A --- B       %% 실선 (화살표 없음)
A -.-> B      %% 점선 화살표
A ==> B       %% 굵은 화살표
```

### classDef

```
classDef highlight fill:#f9f,stroke:#333;
class A highlight;
```

### linkStyle

```
linkStyle 0 stroke:#ff0000,stroke-width:2px;
```

주의: 인덱스는 0부터 시작, 엣지 선언 순서 기준.

## Dangerous Patterns (주의 필요)

| 패턴 | 위험도 | 이유 |
|---|---|---|
| 라벨 안 `/` 문자 | 높음 | 일부 파서에서 경로로 해석 |
| 라벨 안 `()` 문자 | 높음 | 노드 형태 구문과 충돌 |
| 라벨 안 `[]` 문자 | 높음 | 노드 라벨 구문과 충돌 |
| 라벨 안 `\|` 문자 | 높음 | 엣지 라벨 구분자와 충돌 |
| 라벨 안 줄바꿈 | 중간 | `<br/>` 사용 가능하나 환경별 차이 |
| `classDef` + `linkStyle` + subgraph 동시 | 중간 | 인덱스 꼬임 위험 |
| 50개 이상 노드 | 중간 | 렌더 시간 증가, 레이아웃 불안정 |
| 중첩 subgraph | 중간 | 버전별 지원 차이 |

## Style Section

스타일은 다이어그램 끝부분에 모아서 선언한다.

안전한 순서:
1. 노드 선언 + 엣지
2. subgraph
3. `classDef` 정의
4. `class` 적용
5. `linkStyle` (마지막)

스타일 디버깅이 필요하면: 스타일 전체 제거 → 기본 렌더 확인 → 하나씩 복원.
