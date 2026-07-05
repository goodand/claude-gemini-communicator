---
name: codebase-doc-alignment
description: verification-decision-gate family의 code↔document structural alignment specialist. 코드베이스와 문서(논문, MD, PRD, 설계서)의 구조적 정합성을 양방향으로 검사하고 불일치를 파악한다. rule/field-level drift는 doc-code-sync-checker, broader consistency routing은 verification-decision-gate를 사용하라.
---

# Codebase-Doc Alignment

코드 ↔ 문서 정합성 검사 — 불일치를 찾아내고 보고서를 생성.

## 핵심 개념

- **Forward Check**: 문서 → 코드. 문서에 명시된 기능이 코드에 구현되어 있는가?
- **Backward Check**: 코드 → 문서. 코드에 존재하는 기능이 문서에 반영되어 있는가?
- **Drift Detection**: 시간 경과에 따른 코드-문서 괴리 감지
- **Alignment Report**: 정합/불일치 항목별 상세 보고서

## Workflow

### 1. 문서 수집 및 파싱
```bash
# 검사 대상 문서 지정
python3 scripts/check_alignment.py \
  --docs "plans/*.md" "docs/PRD.md" \
  --code "src/"
```

### 2. 정합성 검사 실행
```bash
# 전체 검사 (Forward + Backward)
python3 scripts/check_alignment.py \
  --docs docs/architecture.md \
  --code src/ \
  --output _shared/alignment-reports/

# Forward만 (문서 → 코드)
python3 scripts/check_alignment.py \
  --mode forward \
  --docs docs/PRD.md \
  --code src/

# Backward만 (코드 → 문서)
python3 scripts/check_alignment.py \
  --mode backward \
  --code src/ \
  --docs docs/
```

### 3. 보고서 확인
```bash
# 최신 보고서 확인
cat _shared/alignment-reports/latest.md

# 불일치 항목만 필터
grep -A 3 "❌\|MISMATCH\|MISSING" _shared/alignment-reports/latest.md
```

## 검사 항목

### Forward Check (문서 → 코드)
| 검사 | 설명 |
|------|------|
| 기능 존재 | 문서에 명시된 함수/클래스가 코드에 존재하는가 |
| 인터페이스 일치 | 파라미터, 반환 타입이 문서와 일치하는가 |
| 동작 일치 | 문서에 기술된 동작이 코드 로직과 일치하는가 |
| 의존성 일치 | 문서의 기술 스택이 실제 의존성과 일치하는가 |

### Backward Check (코드 → 문서)
| 검사 | 설명 |
|------|------|
| 미문서화 기능 | 코드에만 존재하고 문서에 없는 기능 |
| 변경 미반영 | 코드가 변경되었으나 문서가 업데이트 안 된 항목 |
| Dead Reference | 문서가 참조하는 코드가 삭제/이동된 경우 |

## 보고서 형식

```markdown
# Alignment Report — 2026-03-13

## Summary
- Total checks: 24
- Aligned: 18 (75%)
- Mismatched: 4 (17%)
- Missing: 2 (8%)

## Mismatches
### ❌ docs/PRD.md:L42 → src/auth.py
- 문서: "OAuth2 + PKCE 인증"
- 코드: JWT 기반 인증만 구현
- 심각도: HIGH
- 권장: 코드에 PKCE 플로우 추가 또는 문서 업데이트

### ❌ src/api.py:rate_limiter() → (문서 없음)
- 코드에 rate limiter 존재하나 문서에 미기재
- 심각도: LOW
- 권장: API 문서에 rate limiting 섹션 추가
```

## 출력 위치

- 정합성 보고서: `_shared/alignment-reports/`
- 체크리스트: `_shared/checklists/`

## Requirements

- Python 3.10+
- 대상 문서: Markdown, PDF, 텍스트 형식 지원

## References

`references/` 디렉토리에 추가 자료를 넣어주세요.
