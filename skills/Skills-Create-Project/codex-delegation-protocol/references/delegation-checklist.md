# Delegation Checklist

Codex에게 위임하기 **전에** 확인해야 할 10항목.

## 체크리스트

### A. 패킷 완전성
- [ ] **A1**: packet.json이 validate 통과하는가? (`packet_builder.py validate`)
- [ ] **A2**: goal이 10자 이상이고 명령형인가?
- [ ] **A3**: done_definition이 기계 검증 가능한가? (커맨드, 파일 존재, 패턴 매칭)

### B. 범위 정합
- [ ] **B1**: allowed_paths가 실제 존재하는 경로인가?
- [ ] **B2**: context_files가 모두 존재하고 읽기 가능한가?
- [ ] **B3**: locked_paths ⊆ allowed_paths 관계가 유지되는가? (dispatch 사용 시)

### C. 프롬프트 품질
- [ ] **C1**: 5-section 구조(Mission/Scope/Context/Constraints/Done)가 모두 있는가?
- [ ] **C2**: 프롬프트에 코드/파일 내용을 직접 삽입하지 않았는가? (경로만 전달)
- [ ] **C3**: Constraints에 모든 제약이 명시되었는가? (암묵적 가정 금지)

### D. 실행 환경
- [ ] **D1**: worktree가 생성되었고 branch가 올바른가? (dispatch 사용 시)

## 판정 기준

| 통과 조건 | 조치 |
|-----------|------|
| 10/10 통과 | 위임 진행 |
| A 또는 C 미통과 | 위임 금지 — 수정 후 재검증 |
| B 또는 D만 미통과 | 경고 후 조건부 진행 가능 |
