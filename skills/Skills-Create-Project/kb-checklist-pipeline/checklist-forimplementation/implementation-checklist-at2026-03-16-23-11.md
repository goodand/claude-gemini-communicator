# kb-checklist-pipeline 구현용 체크리스트

> 역할: branch별 후속 작업을 실제 구현 단위로 내린다.
> source of truth: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-11.md`

## A. Common

- [ ] references를 먼저 저장한다
- [ ] canonical KB를 만든다
- [ ] consistency checklist를 먼저 만든다
- [ ] implementation checklist를 마지막 입력 문서로 둔다

## B. document_output branch

- [ ] 최종 산출물이 `md`, `txt`, `image`인지 확인한다
- [ ] 문서 산출물용 작업 항목만 남긴다
- [ ] TDD 항목은 넣지 않는다
- [ ] evidence가 필요하면 troubleshooting 또는 report만 추가한다

## C. script_output branch

- [ ] 최종 산출물이 실행 코드인지 확인한다
- [ ] `scripts/test_<name>.py`를 먼저 만든다
- [ ] 그 다음 `scripts/<name>.py`를 만든다
- [ ] `--help`, smoke test, evidence 파일 경로를 checklist에 명시한다
- [ ] smoke artifact가 raw report면 diff 전에 metric artifact 변환 단계를 남긴다
- [ ] smoke 이후 debug 메모와 before/after diff 파일 경로를 남긴다

## D. implementation_output branch

- [ ] 최종 산출물이 `md/txt/image`가 아닌 구현물인지 확인한다
- [ ] 해당 구현물의 검증 파일을 먼저 만든다
- [ ] 구현 파일을 그 다음에 만든다
- [ ] smoke/evidence 저장 경로를 남긴다
- [ ] raw smoke artifact를 diff용 metric artifact로 바꾸는 경로를 남긴다
- [ ] debug와 before/after diff 저장 경로를 남긴다
