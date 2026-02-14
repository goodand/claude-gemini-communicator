# Gemini Reviewer Skill — Setup Guide

## 사전 요구사항

1. Python 3.10+
2. `google-genai` 패키지
3. Gemini API Key

## 설치

```bash
pip install google-genai
```

## API Key 설정

```bash
# 방법 1: 환경변수
export GEMINI_API_KEY="your-key-here"

# 방법 2: 프로젝트 루트에 .env 파일
echo 'GEMINI_API_KEY=your-key-here' >> .env
```

무료 API Key: https://aistudio.google.com/apikey

## 도구별 설치

### Codex CLI
```bash
# 글로벌 설치
cp -r skills/gemini-reviewer ~/.codex/skills/

# 또는 프로젝트 로컬 (현재 디렉토리에 두면 자동 인식)
```

### Claude Code
CLAUDE.md에 다음을 추가하면 Claude가 자동으로 이 스킬을 인식합니다:
```markdown
## 사용 가능한 스킬
- `skills/gemini-reviewer/scripts/evaluate.py`: Gemini 코드/문서 리뷰
```

### Cursor / 기타
프로젝트 루트에 `skills/` 디렉토리가 있으면 대부분의 AI 코딩 도구가 인식합니다.

## 검증

```bash
# SDK 연결 테스트
python3 skills/gemini-reviewer/scripts/evaluate.py --file README.md

# 코드 리뷰 테스트
python3 skills/gemini-reviewer/scripts/evaluate.py --file scripts/cli.py --mode code
```
