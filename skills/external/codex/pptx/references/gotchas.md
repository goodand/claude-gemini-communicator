# PPTX 자동화 제작 Gotchas (반복 이슈 및 해결 방안)

이 문서는 탁재현 포트폴리오 프로젝트 및 유사 환경에서 발생하는 반복적인 이슈와 이에 대한 표준 해결 방안을 기록합니다.

## 1. 파일명 인코딩 문제 (NFC vs NFD)
- **증상**: 파일이 분명히 존재함에도 불구하고 Python `os.path.exists()`나 `Image` 로드 시 `FileNotFoundError`가 발생함.
- **원인**: macOS의 한글 자소 분리(NFD) 방식과 타 OS의 완성형(NFC) 방식 간의 충돌.
- **실제 사례**:
  - v1 실행 시 16개 이미지 Warning 발생. 파일명을 추측으로 하드코딩한 것이 근본 원인.
  - 예: `탁재현_이메일수집_정보제공_증명사진.jpg` → 실제 파일명은 `탁재현_증명사진_이력서용사진_삭제_가능.jpg`
  - `Obsidian_DailyNote-2026-01-12 오전 10.15.22.png` 등 공백+한글 조합 파일명 전부 실패.
- **해결 방안**:
  - 모든 파일명을 로드할 때 `unicodedata.normalize('NFC', filename)`을 사용하여 정규화할 것.
  - 정규화된 매핑 테이블(`AssetResolver`) 기반으로 파일을 참조할 것.
  - **코드 작성 전에** `os.walk()`로 전체 자산을 먼저 스캔하여 매핑 테이블을 구축할 것.

## 2. 환경 제약 및 도구 Fallback
- **증상**: `pptxgenjs` (Node.js) 설치 불가 또는 `soffice` (LibreOffice) 명령 부재.
- **실제 사례**:
  - 이전 세션: `npm init` 실행 → 셸 권한 오류로 중단.
  - 현재 세션: 다시 `npm` 시도 → `command not found` → python-pptx 전환. 동일한 실패를 **2세션 연속** 반복.
  - `soffice`, `pdftoppm`, `convert` 모두 부재 → Visual QA 전면 불가.
- **해결 방안**:
  - Node.js 환경이 불안정할 경우 **python-pptx**를 즉시 대안으로 사용할 것.
  - `soffice`가 없어 PDF 변환 및 이미지 QA가 불가능할 경우, **Layout Integrity Report** (좌표 및 Shape 매니페스트 출력) 로직을 스크립트에 포함하여 AI가 텍스트로 레이아웃을 검정할 것.
  - **작업 시작 시 `which node npm soffice pdftoppm`을 한 번에 실행하여 가용 도구를 먼저 파악할 것.**

## 3. 레이아웃 및 여백 표준화
- **증상**: 요소 간 겹침(Overlap), 좌우 여백 불일치, 텍스트 상자 이탈.
- **표준 가이드라인**:
  - **슬라이드 크기**: 13.333" x 7.5" (16:9 Wide) 고정.
  - **최소 여백**: 사방 `Inches(0.5)`.
  - **영역 분할**: 좌측(텍스트/테이블) - 우측(이미지/다이어그램) 2분할 구조를 기본으로 하되, 겹침 방지 로직을 삽입할 것.

## 4. 데이터/이미지 중복(Redundancy) 방지
- **이슈**: 하나의 슬라이드에 동일한 CSV 데이터를 담은 표와 이미지가 중복 사용됨.
- **실제 사례**:
  - v1: S09(복지 나침반)와 S10(자동화 파이프라인)에서 **동일한 이미지**(`새싹해커톤_복지나침반_Diagram-Page.drawio.png`)를 2장에 걸쳐 재사용.
  - v1: 사용 가능한 CSV 8개 중 3개만 활용. 나머지 5개를 방치.
- **해결 방안**:
  - **테이블(Table)**은 정밀한 수치 데이터 전달용으로 사용.
  - **이미지(Image)**는 아키텍처, 스튜디오 샷, 결과 시각화용으로만 사용.
  - 동일한 이미지 파일이 2개 이상의 슬라이드에서 사용되지 않도록 **사용 자산 추적 로직**을 삽입할 것.
  - Visual QA 단계에서 객체들의 메타데이터를 AI에게 주입하여 내용 중복을 검증할 것.

---

# 반복된 Task 패턴 (Recurring Task Patterns)

## 5. 환경 사전 점검 누락 (Pre-flight Check)
- **패턴**: 도구 가용성을 확인하지 않고 계획서를 먼저 작성 → 실행 단계에서 실패 → Fallback 전환 → 계획서 재작성.
- **실제 사례**: PptxGenJS 기반 계획서(v5) 작성 → npm 실패 → python-pptx 전환(v6) → 계획서 재작성. 이 사이클이 2세션에 걸쳐 반복됨.
- **방지책**: 작업 시작 시 아래 명령어를 **반드시 먼저 실행**할 것.
  ```bash
  which node npm npx python3 pip3 soffice pdftoppm convert
  python3 -c "import pptx; print(pptx.__version__)"
  ```

## 6. 파일명 추측 후 하드코딩 (Asset Guessing)
- **패턴**: 실제 파일 시스템을 스캔하지 않고 파일명을 추측하여 코드에 직접 작성 → 실행 시 `FileNotFoundError` 또는 Warning 다수 발생 → 개별 수정 반복.
- **실제 사례**:
  - v1에서 S01 프로필 이미지 파일명 오류 → `list_dir`로 확인 후 수정.
  - 그러나 S07~S19에서도 동일하게 추측 기반으로 작성 → 실행 시 16개 Warning.
- **방지책**: **코드 작성 전에** `os.walk()` 또는 `find` 명령으로 전체 자산 매니페스트를 생성하고, 이를 기반으로 코드를 작성할 것.

## 7. SVG 포맷 미지원 인지 부재
- **패턴**: python-pptx에 SVG 파일을 삽입 시도 → PIL의 `UnidentifiedImageError` 발생.
- **실제 사례**: `before_after_architecture_6pairs.svg` 삽입 시도 → 크래시.
- **방지책**:
  - python-pptx는 **PNG, JPEG, GIF, BMP, TIFF만 지원**함을 인지할 것.
  - SVG 파일이 있을 경우 사전에 `cairosvg` 또는 브라우저 캡처를 통해 PNG로 변환한 뒤 삽입할 것.
  - `add_image()` 함수에서 확장자 검사 로직을 포함할 것.

## 8. Visual QA 의무 미이행
- **패턴**: SKILL.md가 명시적으로 "Assume there are problems. Your job is to find them."이라고 요구했음에도 QA를 건너뜀.
- **실제 사례**:
  - `soffice` 부재를 이유로 Visual QA 자체를 전면 생략.
  - Content QA(`python -m markitdown output.pptx`)조차 실행하지 않음.
  - 사후 자가 평가에서 스스로를 "Excellent"로 평가 → 사용자가 지적.
- **방지책**:
  - `soffice` 부재 시 대안 우선순위: (1) Layout Integrity Report → (2) Content QA via markitdown → (3) 슬라이드별 좌표 교차 검증.
  - **Visual QA는 생략 불가**. 도구가 없으면 대안을 찾되, 절대 건너뛰지 말 것.
  - QA 결과를 로그로 남기고, 1회 이상의 fix-and-verify 사이클을 반드시 수행할 것.

## 9. 함수 시그니처 불일치 (Function Signature Mismatch)
- **패턴**: 함수를 정의한 뒤 호출부를 작성할 때 시그니처를 재확인하지 않아 `TypeError` 발생.
- **실제 사례**: `add_txt()` 함수에 `align` 파라미터 없이 정의 → 호출 시 `align="center"` 전달 → TypeError 크래시.
- **방지책**: 함수 정의와 호출부를 동시에 작성하거나, 호출 전에 시그니처를 반드시 확인할 것.

## 10. Python 패키지 vs 시스템 라이브러리 (pip install ≠ 사용 가능)
- **증상**: `pip3 install`은 성공했음에도 불구하고 `import` 시 `OSError` 또는 `ModuleNotFoundError` 발생.
- **원인**: Python 패키지는 설치되었으나, 해당 패키지가 의존하는 시스템 레벨 C-라이브러리(예: `libcairo`)가 부재함.
- **실제 사례**: `cairosvg` 설치 성공 후 실행 시 `no library called "cairo"` 에러로 중단.
- **해결 방안**:
  - 시스템 바인딩이 포함된 패키지는 설치 후 **반드시 `python3 -c "import [module]"`로 정상 로드 여부를 즉시 검증**할 것.
  - 시스템 패키지 설치가 불가능한 환경(권한 제한 등)이라면 브라우저 캡처나 순수 Python 대안을 신속히 탐색할 것.

## 11. 이미지 Aspect Ratio 및 자동 높이 조절 이슈
- **증상**: 이미지의 `width`만 지정하여 삽입했을 때, 원본 비율에 따라 `height`가 비정상적으로 커져 슬라이드를 이탈하거나 하단 요소와 겹침.
- **원인**: `python-pptx`의 `add_picture`는 하나의 차원만 주어지면 원본 가로세로비를 유지하며 다른 차원을 자동 계산함.
- **실제 사례**: S01 프로필 이미지와 S03, S05 RAG 분석 이미지들이 하단 여백을 이탈하거나 겹침(Overlap) 발생.
- **해결 방안**:
  - `add_img()` 함수에 **`max_h` (최대 허용 높이) 클램핑 로직**을 반드시 포함할 것.
  - `pic.height`가 `max_h`를 초과할 경우 비율을 유지하며 강제 Re-size 수행.

## 12. 문서-코드 간 데이터 Drift (Manual Data Entry)
- **증상**: 계획서나 검증 요청문에 작성한 "파일명 목록"이 실제 파일 시스템과 일치하지 않아 분석에 혼선 발생.
- **원인**: `os.walk()` 스캔 결과를 문서로 옮기는 과정에서 수동 편집으로 인한 오타 또는 누락.
- **실제 사례**: 검증 요청문에 `image12~15.png`를 정답 목록에 넣었으나 실제로는 존재하지 않았고, Obsidian 파일명도 오전/오후가 반대로 기재됨.
- **해결 방안**:
  - 파일명 등 데이터 진실(Truth-source)은 **코드로 직접 스캔(`AssetResolver`)한 결과**만을 믿을 것.
  - 문서에 수동으로 기재된 목록은 "참조용"일 뿐이며, 코드 작성 시에는 실시간 파일 시스템 상태를 동력원으로 삼을 것.

## 13. Visual QA의 기계적 회피 (QA Inertia)
- **증상**: 텍스트 로그나 좌표 레포트만으로 "검증 완료"를 선언하고 실제 시각적 확인을 미룸.
- **실제 사례**: 2세션 연속으로 시각적 검증을 건너뛰고 "Excellent"로 자평했다가 사용자 비판 수신.
- **해결 방안**:
  - **브라우저 서브에이전트**를 활용해 생성된 결과물 또는 변환 과정을 반드시 눈으로 확인(Visual Review)할 것.
  - 텍스트 리포트가 통과되더라도 폰트 렌더링, 색상 대비 등 시각적 품질은 별도의 스크린샷 검수를 수행할 것.
