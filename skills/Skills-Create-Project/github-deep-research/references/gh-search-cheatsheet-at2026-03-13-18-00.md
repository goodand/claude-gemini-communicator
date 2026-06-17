# gh search 치트시트

## 코드 검색

```bash
# 특정 함수/패턴의 실제 사용 예시
gh search code "from langfuse import Langfuse" --language python --limit 20

# 특정 파일명 패턴
gh search code --filename "tmux.conf" "send-keys" --limit 10

# 조직/사용자 범위 제한
gh search code "worktree" --owner=anthropics --limit 10
```

## 이슈/PR 검색

```bash
# 키워드로 이슈 검색
gh search issues "tmux capture-pane encoding" --limit 10 --sort updated

# 특정 리포에서 관련 PR 검색
gh search prs "worktree parallel" --repo=git/git --limit 10

# 라벨/상태 필터
gh search issues "langfuse codex" --state open --sort reactions
```

## 리포지토리 검색

```bash
# 유사 프로젝트 탐색
gh search repos "agent tmux" --language python --sort stars --limit 10

# README 빠르게 확인
gh repo view owner/repo --json readme --jq '.readme' | head -50

# 리포 상세 정보
gh repo view owner/repo --json description,stargazerCount,issues
```

## 딥리서치 4단계 패턴

```bash
# Step 1: 넓은 검색으로 후보 수집
gh search code "pattern" --limit 30 > /tmp/candidates.txt

# Step 2: 상위 결과의 실제 코드 확인
gh api repos/owner/repo/contents/path/to/file | jq -r '.content' | base64 -d

# Step 3: 해당 리포의 이슈/PR에서 맥락 파악
gh search issues "keyword" --repo owner/repo --limit 5

# Step 4: 결과 교차검증 및 정리
python3 scripts/deep_search-at2026-03-13-18-00.py --query "keyword" --scope all --output report.md
```

## 검색 전략 테이블

| 목적 | 검색 전략 |
|------|-----------|
| 사용법 파악 | `gh search code "import X"` → 실제 코드 확인 |
| 에러 해결 | `gh search issues "에러 메시지"` → 해결된 이슈 |
| 베스트 프랙티스 | 스타 수 높은 리포의 코드 패턴 참고 |
| 최신 동향 | `--sort updated`로 최근 활동 확인 |
| 의존성 분석 | `gh search code "require(X)"` + `--language` 필터 |

## `--` 구분자 사용법

제외 조건(negation qualifier)을 사용할 때는 `--` 구분자가 필수:

```bash
# 잘못된 사용 (에러 발생)
gh search code "langfuse" -language:go

# 올바른 사용
gh search code -- "langfuse -language:go"
```

이 규칙은 `gh search code`, `gh search issues`, `gh search prs`, `gh search repos` 모두 동일.

## 고급 필터

```bash
# 파일 크기 제한
gh search code "pattern" --filename "*.py" --limit 20

# 날짜 범위 (이슈)
gh search issues "bug" --created ">2026-01-01" --sort created

# 리액션 수 기준 (인기 이슈)
gh search issues "feature request" --sort reactions --limit 10

# 머지된 PR만
gh search prs "fix" --merged --sort updated --limit 10
```
