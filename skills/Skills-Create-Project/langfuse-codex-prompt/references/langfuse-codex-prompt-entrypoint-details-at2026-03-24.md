# Langfuse-Codex Prompt — Entrypoint Details

- recorded_at: `2026-03-24`

## 핵심 개념

- **Langfuse Prompt**: 버전 관리되는 프롬프트 템플릿 (변수 치환 지원)
- **Codex CLI**: 비대화형 코딩 에이전트 (프롬프트 → 코드 생성)
- **Trace**: 실행 기록 (입력 프롬프트, 출력, 지연시간, 비용)
- **Score**: trace/span에 부착되는 평가 점수 (NUMERIC/BOOLEAN/CATEGORICAL)

## 목표 Scripts 인터페이스

> 아래 scripts는 미구현 상태. 구현 전까지 curl/Python SDK를 직접 사용한다.

| Script | 목적 |
|--------|------|
| `fetch_prompt.py` | Langfuse에서 프롬프트 조회 |
| `run_with_prompt.py` | 변수 치환 후 Codex 실행 + trace 자동 기록 |
| `log_trace.py` | 수동 trace 기록 |
| `manage_prompts.py` | 프롬프트 CRUD + trace 조회 |

## Workflow

### 1. Langfuse에서 프롬프트 가져오기

```bash
curl -s "https://cloud.langfuse.com/api/public/v2/prompts/codex-review" \
  -H "Authorization: Bearer $LANGFUSE_PUBLIC_KEY" | jq '.prompt'
```

### 2. 변수 치환 후 Codex 실행

```bash
# 프롬프트 템플릿: "{{file}}을 리뷰하고 {{focus}} 관점에서 개선점을 제안해줘"
# scripts 구현 후:
python3 scripts/run_with_prompt.py \
  --prompt-name codex-review \
  --var file=src/auth.py \
  --var focus=보안 \
  --model gpt-5.3-codex
```

### 3. 결과를 Langfuse에 트레이스로 기록

```bash
# scripts 구현 후:
python3 scripts/log_trace.py \
  --name "codex-review-auth" \
  --input "프롬프트 내용" \
  --output "Codex 응답" \
  --metadata '{"model":"gpt-5.3-codex","file":"src/auth.py"}'
```

## 환경 설정

```bash
# .env에 추가
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com  # 또는 셀프호스트 URL
```

## 프롬프트 템플릿 예시

```yaml
codex-review:
  template: |
    다음 파일을 리뷰해줘: {{file}}
    관점: {{focus}}
    출력 형식: markdown 리스트
  variables: [file, focus]

codex-refactor:
  template: |
    {{file}}을 리팩토링해줘.
    목표: {{goal}}
    제약: 기존 API 인터페이스 유지
  variables: [file, goal]
```

## Requirements

- Python 3.10+
- `langfuse` Python SDK
- `codex` CLI 로그인 상태
- Langfuse 계정 (클라우드 또는 셀프호스트)

## Evaluation hookup 패턴

agent-tool-benchmark에서 계산한 메트릭을 Langfuse score로 push하는 패턴:

```python
from metric_formulas import ast_accuracy
from langfuse import Langfuse

langfuse = Langfuse()
value = ast_accuracy(predictions)
langfuse.create_score(
    trace_id=tid,
    name="ast_accuracy",
    value=value,
    data_type="NUMERIC",
)
```

상세 score taxonomy와 dataset-run 패턴은 KB 참조:
→ `knowledge_bases/langfuse-agent-evaluation-kb-at2026-03-24.md`
