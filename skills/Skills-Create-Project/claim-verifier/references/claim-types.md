# Claim Types

## Claim 분류 초안

- 구현 존재 claim: "지원한다", "구현됐다"
- 상태 claim: "완료됐다", "실행된다", "동작한다"
- 정합성 claim: "문서와 일치한다", "테이블과 코드가 맞다"
- artifact claim: "파일이 생성된다", "로그가 남는다"
- 경계 claim: "이 skill은 X를 하지 않는다", "Y만 소유한다"

## 판정 상태

- `true`: 코드/문서/파일 근거가 claim을 직접 지지
- `false`: 반대 근거가 명확
- `partial`: 일부만 충족
- `unverifiable`: 현재 근거로는 판정 불가

## Evidence Types

- `file_exists`: 파일 존재 (is_file 기준)
- `dir_exists`: 디렉토리 존재
- `keyword_match`: 코드/문서 내 키워드 매칭 (라인 번호 포함)

> **Note**: pairwise doc↔code 비교 (`pairwise_sync`, `pairwise_drift`)는 doc-code-sync-checker 영역.
> claim-verifier는 consistency claim에 대해 partial/unverifiable 판정 후 doc-code-sync-checker로 위임한다.
