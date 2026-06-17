# Troubleshooting

## CASE-001 Live Context Beats JSONL Repair

- symptom: `resume_precheck.py`는 pass인데 `Selected N lines from ... in Visual Studio Code`가 반복된다
- interpretation: stored session corruption보다 live IDE selection context가 더 유력하다
- action: JSONL fix보다 선택 해제, 관련 탭 닫기, 최소 입력 retry를 먼저 한다

## CASE-002 Raw Append Corrupts settings.json

- symptom: `~/.claude/settings.json` 수정 후 별도 config parse 오류가 생긴다
- interpretation: `>> ~/.claude/settings.json` 같은 append로 JSON object가 중복됐을 가능성이 높다
- action: settings는 항상 full JSON parse 후 merge-write로 수정한다

## CASE-003 Feature Existence Does Not Prove Exact Key

- symptom: selection context feature는 의심되는데 exact settings key를 못 찾는다
- interpretation: feature existence와 exact key는 별개다
- action: official issue는 symptom corroboration 용도로만 쓰고, exact key는 runtime에서 직접 검증한다
