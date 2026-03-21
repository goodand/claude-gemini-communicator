# Markdown Artifact Writing Patterns

- scope: `workspace-artifact-production-process`에서 재사용 가능한 MD 작성 규칙과 노하우 집약본
- source notes: `phase-guide.md`, `progressive-context-injection.md`, `skill-directory-structure.md`, `practical-lessons.md`

## What This Covers

- `SKILL.md`
- `references/*.md`
- `knowledge_bases/*.md`
- `checklist-forconsistency-evaluation/*.md`
- 일반 task/progress/reference 문서

## Core Rules

- 먼저 `무엇을 source of truth로 둘지` 고정하고 그 다음 문서를 쓴다.
- entrypoint와 deep context를 한 파일에 섞지 않는다.
- 같은 내용을 `SKILL.md`, `references/`, `knowledge_bases/`에 중복하지 않는다.
- 파일 역할이 다르면 문체도 다르게 쓴다.
  - `SKILL.md`: 언제 쓰는가 + 어떤 순서로 하는가
  - `references/`: 상세 규칙, 사례, troubleshooting
  - `knowledge_bases/`: 채택된 설계와 canonical takeaways
  - `checklist`: 판정 항목

## SKILL.md Rules

- frontmatter는 Layer 0 metadata contract다.
- `name`과 `description`은 trigger와 역할을 닫아야 한다.
- 본문은 entrypoint만 유지하고, 상세 규칙은 링크로 내린다.
- `quick_validate` line-count warning이 나오면 문장 압축보다 split을 우선한다.
- split 후에는 원문 의미를 유지하고, entrypoint에는 짧은 설명과 링크만 남긴다.

## Reference Writing

- 조사 원자료, 세부 규칙, 예외, troubleshooting은 `references/`에 둔다.
- reference는 넓게 써도 되지만, 나중에 KB로 올릴 수 있게 source/결론을 분리해 둔다.
- 실험 후 새 교훈이 생기면 `troubleshooting.md`와 관련 reference에 먼저 남긴다.
- reference끼리도 역할이 다르면 `families/`, `indexes/`, 단일 note를 구분한다.

## Issue And Evidence Storage

- smoke/test raw evidence는 `references/*smoke*`, 로그, evidence ledger 같은 실행 증거 층에 남긴다.
- multi-file smoke raw archive는 `logs/smoke/<command>/<timestamp>/...`에 분리하고, smoke report는 그 `archive_dir`를 링크한다.
- 사람이 읽는 issue narrative는 `references/troubleshooting.md`의 `CASE-XXX` 형식으로 적는다.
- entrypoint에는 해결 규칙 1줄만 올리고, 상세는 troubleshooting case로 보낸다.
- `references/fixtures/`는 sample input/output bundle 계층이며 issue log 저장소가 아니다.
- 자세한 저장 경계는 `issue-evidence-storage-rule-at2026-03-21-16-33.md`, archive layout은 `smoke-archive-layout-rule-at2026-03-21-19-06.md`를 따른다.

## KB Writing

- KB는 reference를 다시 적는 문서가 아니라 채택된 설계를 구조화한 문서다.
- checklist와 code의 source of truth가 될 KB에는 `Canonical Design Takeaways`를 둔다.
- 조사 자산이 많으면 `research_index_kb`, 채택 설계를 함께 담으면 `hybrid_kb`, 좁은 기준만 남기면 `canonical_design_kb`로 본다.

## Checklist Writing

- consistency checklist는 `무엇이 맞아야 하는가`를 묻는다.
- implementation checklist는 정말 필요할 때만 쓰고, 과하면 TDD로 내려도 된다.
- checklist는 KB의 compiled view이지 source of truth가 아니다.

## Naming And Linking

- reference/KB/checklist 문서는 분 단위 타임스탬프 파일명을 기본으로 둔다.
- 링크는 모호한 "자세한 내용은 참고" 대신 정확한 파일 포인터로 쓴다.
- active artifact rename/delete/cleanup 판단은 즉흥적으로 하지 말고 lifecycle rule로 넘긴다.

## Writing Anti-Patterns

- 자료 조사 없이 바로 초안 작성
- `SKILL.md`에 deep context를 그대로 붙여 넣기
- reference 내용을 KB와 entrypoint에 중복 복사
- line limit 초과를 억지 압축으로 해결
- 문서 규칙을 코드/validator와 전혀 연결하지 않기

## Practical Heuristics

- 문서는 항상 `역할`, `입력`, `판정`, `산출물` 순서로 읽히게 쓴다.
- 규칙 문서는 예시보다 판정 기준을 먼저 둔다.
- troubleshooting 규칙은 entrypoint에 1줄만 올리고, 상세는 case 문서로 보낸다.
- 반복해서 설명되는 규칙은 새 reference 하나로 승격해 재사용한다.
