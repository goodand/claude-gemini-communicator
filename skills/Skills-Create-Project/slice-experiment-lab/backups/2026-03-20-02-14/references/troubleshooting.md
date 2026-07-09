# slice-experiment-lab troubleshooting

- triad artifact는 path만 저장하지 말고 실제 파일 존재 여부까지 evaluator에서 확인한다
- `quick_validate_status`는 로그 원문 전체보다 `passed|failed`로 먼저 정규화하는 편이 재사용성이 높다
- next-slice 후보는 공용 process에서 추론하지 말고 대상 skill checklist에서 받아온다
- `capture-smoke-command`는 stdout JSON이 있으면 그 안의 `status`도 같이 본다
- triad naming은 `contract-smoke / validation-smoke / invalid-validation-smoke` suffix를 고정하는 편이 후속 evaluator와 잘 맞는다
