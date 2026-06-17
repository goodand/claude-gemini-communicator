---
name: claim-verifier
description: >-
  verification-decision-gate family의 claim verification specialist. Use this
  skill when a natural-language or document claim must be decomposed into
  verifiable units and checked against code, files, or repo artifacts.
  multi-concern consistency judgment이나 next-step gate는
  verification-decision-gate를 사용하라.
---

# Claim Verifier

repo 안의 사실 판정기. 자연어 주장을 원자화하고, 증거 없는 확신을 금지하며, unverifiable을 별도 상태로 보존한다.

## When to use

- 외부 피드백이나 리뷰 코멘트가 사실인지 확인할 때
- "구현됐다", "지원한다", "완료됐다" 같은 주장을 증거로 검증할 때
- 문서 서술과 실제 artifact 존재 여부를 대조할 때
- checklist/done_definition과 코드 실제 상태의 정합성을 판정할 때
- `artifact-lifecycle-manager`가 stale candidate로 올린 claim-heavy reference를 2차 semantic recheck할 때

## Rules

1. **claim을 최소 검증 단위로 쪼갠다.** "구현됐다 + 테스트된다 + 문서와 맞다"가 섞여 있으면 분리한다.
2. **line evidence를 붙인다.** "대충 그런 것 같다"는 판정 금지. 가능하면 파일 경로 + 라인 번호, 불가능하면 file-level evidence + 이유를 명시한다.
3. **문서 존재 ≠ 구현 존재.** README에 적혀 있다고 구현된 게 아니다. 코드 증거와 문서 증거를 별도로 수집한다.
4. **unverifiable ≠ false.** 증거 부족과 반대 증거는 다르다. 현재 근거로 판정할 수 없으면 unverifiable로 보존한다.
5. **판정마다 후속 조치를 남긴다.** false면 무엇을 고칠지, partial이면 무엇이 빠졌는지, unverifiable이면 무엇을 더 찾아야 하는지.

> 기본 단위는 "문서 있음"이 아니라 "근거가 무엇인지"다.

## Ecosystem

```
agent-task-packet (실행 계약)
    ↓ 실행 결과
claim-verifier (관측/증거 → 실행 계약 정합성 판정)
    ↓ 정량화 필요시              ↑ consistency claim 위임
agent-tool-benchmark (메트릭 수식)   doc-code-sync-checker (pairwise drift)
```

공간 모델 #4: 관측/증거 공간 → 사실 판정/claim verification 공간.

- `reference freshness audit`의 1차 stale candidate 탐지는 `artifact-lifecycle-manager`가 맡고, 이 skill은 claim-heavy reference의 2차 semantic recheck를 맡는다.
- consistency claim(문서↔코드 일치)은 partial/unverifiable 판정 후 `doc-code-sync-checker`로 위임한다.
- image evidence와 text judgment를 human-facing review surface와 machine-truth manifest로 함께 층화하는 multimodal review structuring은 `image-text-cot-review`로 handoff한다.

상세 워크플로와 CLI 사용법은 [entrypoint 상세 안내](references/claim-verifier-entrypoint-details-at2026-03-25.md)를 따른다.

## Scripts

- `scripts/claim_verifier.py` — extract / verify / report / table / batch (`--help` 지원)
- `scripts/claim_lint.py` — 중간 산출물 lint: claims / results 품질 검사 + follow-up skeleton 생성 (`--help` 지원)

## References

- [references/claim-verifier-entrypoint-details-at2026-03-25.md](references/claim-verifier-entrypoint-details-at2026-03-25.md) — 워크플로 상세, CLI 사용법
- [references/claim-types.md](references/claim-types.md) — claim 분류
- [references/verification-checklist.md](references/verification-checklist.md) — 증거 수집/판정 체크리스트
- [references/troubleshooting.md](references/troubleshooting.md) — 실전 검증 케이스 (7건)
- [references/improvement-priorities-at2026-03-26.md](references/improvement-priorities-at2026-03-26.md) — 개선 방향 우선순위

## Knowledge Bases

- [knowledge_bases/claim-verifier-knowledge_base-at2026-03-16.md](knowledge_bases/claim-verifier-knowledge_base-at2026-03-16.md) — GitHub 논문 리서치 URL KB
