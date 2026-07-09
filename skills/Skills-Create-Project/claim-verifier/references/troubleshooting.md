# Troubleshooting — claim-verifier

## CASE-001: 문서 존재를 구현 존재로 오판

- **증상**: README나 reference에 적혀 있다는 이유만으로 claim을 true로 판정
- **원인**: artifact 존재와 코드 구현 존재를 분리하지 않음
- **해결법**: 문서 증거와 코드 증거를 별도 열로 수집. `is_file()` 기준으로 파일/디렉토리 구분
- **교훈**: claim-verifier의 기본 단위는 "문서 있음"이 아니라 "근거가 무엇인지"다

## CASE-002: keyword hit를 구현 근거로 과신

- **증상**: 코드에 keyword가 언급만 돼 있어도 "구현됨"으로 판정
- **원인**: keyword_match만으로 implementation claim을 true 판정
- **해결법**: keyword-only → `partial` 판정. `true`는 keyword + file evidence 모두 필요
- **교훈**: 언급(mention)과 구현(implementation)은 다르다

## CASE-003: unverifiable을 false로 밀어버림

- **증상**: 증거를 못 찾으면 "없으니까 false"로 판정
- **원인**: 증거 부족(unverifiable)과 반대 증거 발견(false)을 혼동
- **해결법**: evidence 없음 → unverifiable, 반대 evidence 있음 → false. 별도 분기 필수
- **교훈**: "못 찾았다"와 "반대를 찾았다"는 다른 판정이다

## CASE-004: consistency claim이 단순 grep으로 안 닫힘

- **증상**: "문서와 코드가 일치한다" claim을 keyword grep으로 판정하려 함
- **원인**: consistency claim은 문서 한쪽 + 코드 한쪽을 pair로 대조해야 하는데 단일 검색으로 처리
- **해결**: doc-code-sync-checker로 위임. claim-verifier는 consistency claim에 partial/unverifiable + follow_up "doc-code-sync-checker로 정밀 비교 필요" 반환
- **교훈**: 일치 여부는 양쪽을 모두 읽어야 판정 가능

## CASE-005: follow-up이 약해짐

- **증상**: verdict는 있는데 "그래서 뭘 더 확인/수정해야 하는지"가 빈약
- **원인**: follow-up 문자열이 고정 패턴 3종으로 한정됨
- **현재 한계**: claim 내용 기반 구체적 안내 부족
- **교훈**: 판정 없는 follow-up은 쓸모없고, follow-up 없는 판정도 불완전하다

## CASE-006: 외부 피드백 묶음 처리가 매번 수작업

- **증상**: Codex/Gemini 피드백 4건 같은 묶음을 받을 때 매번 수동 정리 필요
- **원인**: batch 입력 포맷이 고정돼 있지 않음
- **해결**: `verify_batch()` + `batch` CLI 서브커맨드. str/dict 혼합 입력, 자동 id 부여, 자동 type 분류
- **교훈**: 실전에서는 묶음 입력이 단건보다 훨씬 잦다

## CASE-007: 디렉토리 존재를 파일 존재로 오판

- **증상**: `src/` 디렉토리가 있으면 `src/missing.py` claim도 true로 판정
- **원인**: `Path.exists()`가 디렉토리에도 True 반환
- **해결법**: `Path.is_file()` 사용. 디렉토리는 `dir_exists` evidence type으로 분리
- **교훈**: 파일 존재와 디렉토리 존재는 다른 증거 유형이다
