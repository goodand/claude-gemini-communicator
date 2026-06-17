# GitHub Search Report — claim-verifier

## 사용자 의도 파악

- 목표: 자연어/문서 claim을 검증 가능한 단위로 쪼개고, 근거를 수집해 true/false/partial/unverifiable로 판정하는 skill 설계에 필요한 GitHub 레퍼런스 수집
- 제외: 일반 뉴스 fact-checking UI, 소셜 전용 moderation 시스템

## Shortlist

### 1. Yixiao-Song/VeriScore
- URL: https://github.com/Yixiao-Song/VeriScore
- 선택 이유:
  - claim extraction -> evidence retrieval -> claim verification 3단계 파이프라인이 claim-verifier의 핵심 구조와 가장 직접적으로 닿음
  - binary/ternary verdict와 component 분리가 명확

### 2. BharathxD/ClaimeAI
- URL: https://github.com/BharathxD/ClaimeAI
- 선택 이유:
  - `claim_extractor/`, `claim_verifier/`, `fact_checker/` 모듈 분리가 잘 보임
  - 최종 report 생성 흐름이 skill의 report 단계 설계에 도움

### 3. mbzuai-nlp/fire
- URL: https://github.com/mbzuai-nlp/fire
- 선택 이유:
  - iterative retrieval and verification 구조
  - claim별 검색 깊이를 동적으로 조절하는 아이디어가 evidence loop 설계에 유효

### 4. shmsw25/FActScore
- URL: https://github.com/shmsw25/FActScore
- 선택 이유:
  - atomic fact decomposition과 labeled fact output이 claim granularity 설계에 도움

### 5. tatsu-lab/conformal-factual-lm
- URL: https://github.com/tatsu-lab/conformal-factual-lm
- 선택 이유:
  - sub-claim splitting과 후속 검증/annotation 흐름이 분리돼 있음

### 6. johnlindquist/fact-checker-verifier.md
- URL: https://gist.github.com/johnlindquist/e1d7aea1cadc59a8e0de003648e98f17
- 선택 이유:
  - Claude Code agent 형식으로 claim extraction -> source verification -> rewrite/report 책임이 정리돼 있음
  - 단, 소셜 미디어 claim 검증 편향이 강해 그대로 복사하면 안 됨

## Design Takeaways

- 필수 모듈은 `claim extraction`, `evidence retrieval`, `verification`, `report`
- 판정 스키마는 최소 `true/false/partial/unverifiable`
- claim 단위가 너무 크면 evidence 매칭이 흐려지고, 너무 작으면 과도한 분절이 발생
- 최종 보고서는 claim별 evidence와 overall summary를 둘 다 가져야 함

## Reject / Hold

- 일반 fact-checking 웹앱은 많지만, 코드/문서 artifact를 evidence로 삼는 repo는 드묾
- 따라서 검색 결과는 "기존 fact-check pipeline" + "Claude agent prompt"를 조합해 설계로 환원해야 함
