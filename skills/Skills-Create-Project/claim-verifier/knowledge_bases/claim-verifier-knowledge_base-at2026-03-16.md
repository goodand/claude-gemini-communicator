# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-16`
- updated_at: `2026-03-16` (v0.1.0: initial claim-verifier KB)
- format: `- [한 줄 설명](URL)`
- generation_method: `JSONL intent 복원 + GitHub repository search + 후보 축약`
- total_urls: `6`
- paper_like_urls: `4`
- other_urls: `2`

## Document Map

| 문서 | 역할 |
|------|------|
| [SKILL.md](../SKILL.md) | skill 목적 · 워크플로우 |
| `claim-verifier-knowledge_base-at2026-03-16.md` (이 파일) | GitHub URL 인덱스 |
| [claim-verifier-github-search-at2026-03-16.md](../../github-deep-research/references/claim-verifier-github-search-at2026-03-16.md) | 후보 수집 및 선택 근거 |
| [claim-doc-sync-intent-from-jsonl-at2026-03-16.md](../../_shared/reference-inbox/claim-doc-sync-intent-from-jsonl-at2026-03-16.md) | 메모리 기반 의도 복원 |

## Table of Contents
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Paper-like URLs

- [VeriScore - claim extraction, evidence retrieval, claim verification 3단계 파이프라인](https://github.com/Yixiao-Song/VeriScore)
  - sources: `github search`
  - agent: `A00`
  - taxonomy: `[[claim_pipeline]] · extraction/retrieval/verification`
  - key_idea: claim을 원자 단위로 추출한 뒤 evidence retrieval과 verification을 분리한다.
  - execution_conditions: search API 또는 대체 evidence source 필요
  - pseudocode_3lines:
    - 1) 입력 텍스트를 claim 목록으로 분해한다.
    - 2) claim마다 evidence를 수집한다.
    - 3) supported/contradicted/inconclusive로 판정한다.

- [FIRE - iterative retrieval and verification agent](https://github.com/mbzuai-nlp/fire)
  - sources: `github search`
  - agent: `A00`
  - taxonomy: `[[iterative_verification]] · retrieval loop`
  - key_idea: claim마다 retrieval을 고정 횟수로 하지 않고 confidence 기반으로 반복 깊이를 조절한다.
  - execution_conditions: iterative loop 관리 필요
  - pseudocode_3lines:
    - 1) 초기 evidence를 검색한다.
    - 2) confidence가 낮으면 추가 검색을 반복한다.
    - 3) 충분하면 verdict를 종료한다.

- [FActScore - atomic fact decomposition and labeling](https://github.com/shmsw25/FActScore)
  - sources: `github search`
  - agent: `A00`
  - taxonomy: `[[atomic_claims]] · fact labeling`
  - key_idea: long-form text를 atomic fact로 나눈 뒤 각 fact를 별도 label로 관리한다.
  - execution_conditions: claim granularity 설계 필요
  - pseudocode_3lines:
    - 1) 텍스트를 atomic facts로 분해한다.
    - 2) fact별 라벨을 부여한다.
    - 3) 전체 스코어 또는 verdict를 집계한다.

- [conformal-factual-lm - sub-claim splitting and annotated verification flow](https://github.com/tatsu-lab/conformal-factual-lm)
  - sources: `github search`
  - agent: `A00`
  - taxonomy: `[[subclaim_flow]] · split/annotate/verify`
  - key_idea: sub-claim splitting과 후속 검증 단계를 분리해 calibration 가능한 파이프라인을 만든다.
  - execution_conditions: sub-claim intermediate artifact 저장 필요
  - pseudocode_3lines:
    - 1) 출력 텍스트를 sub-claim jsonl로 저장한다.
    - 2) claim별 검증/annotation을 수행한다.
    - 3) 결과를 다시 집계한다.

## Other research References URLs

- [ClaimeAI - claim_extractor / claim_verifier / fact_checker 모듈 분리](https://github.com/BharathxD/ClaimeAI)
  - sources: `github search`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) claim_extractor가 testable claim을 만든다.
    - 2) claim_verifier가 online evidence를 대조한다.
    - 3) fact_checker가 최종 report를 만든다.

- [fact-checker-verifier gist - Claude Code agent prompt 형태의 claim verification 예시](https://gist.github.com/johnlindquist/e1d7aea1cadc59a8e0de003648e98f17)
  - sources: `github search`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 검증할 claim을 식별한다.
    - 2) authoritative source를 우선 수집한다.
    - 3) corrected summary와 source list를 출력한다.
