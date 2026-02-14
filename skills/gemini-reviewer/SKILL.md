---
name: gemini-reviewer
description: 코드나 문서를 작성/수정한 후 Gemini에게 리뷰를 요청할 때 사용합니다. 코드 리뷰, 계획 평가, 설계 문서 검토에 적합합니다.
---

# Gemini Reviewer Skill

코드나 문서를 Gemini에게 평가받는 크로스-에이전트 리뷰 스킬입니다.

## 사용 시점

다음 상황에서 이 스킬을 사용하세요:
- 코드 파일(.py, .js, .ts 등)을 작성/수정한 후
- 설계 문서나 계획을 완성한 후
- 사용자가 "리뷰해줘", "평가해줘", "검토해줘"라고 요청했을 때

## 사용 방법

### 1. 파일 리뷰
```bash
python3 skills/gemini-reviewer/scripts/evaluate.py --file <파일경로>
```

### 2. 코드 리뷰 (코드 파일 자동 감지)
```bash
python3 skills/gemini-reviewer/scripts/evaluate.py --file <파일경로> --mode code
```

### 3. 텍스트 직접 전달
```bash
echo "리뷰할 내용" | python3 skills/gemini-reviewer/scripts/evaluate.py --mode doc
```

### 4. 커스텀 프롬프트
```bash
python3 skills/gemini-reviewer/scripts/evaluate.py --file <파일경로> --prompt "보안 취약점만 집중적으로 분석해줘"
```

## 결과 처리

- 리뷰 결과는 stdout으로 출력됩니다.
- `--save` 플래그를 추가하면 `gemini_feedback.md`에도 저장됩니다.
- 결과를 사용자에게 요약해서 전달하세요.

## 사전 요구사항

- `GEMINI_API_KEY` 환경변수 설정 필요
- Python 3.10+
- `google-genai` 패키지 (`pip install google-genai`)
