# Gemini 프롬프트 템플릿

이 문서는 Gemini (또는 다른 LLM)에게 효과적으로 질문하기 위한 프롬프트 템플릿을 제공합니다.

## 기본 구조

```
# 역할 정의
당신은 [전문가 역할] 입니다.

# 컨텍스트 제공
현재 상황: [문제 정의]
목표: [달성하려는 것]

# 데이터 제공
[구조화된 데이터]

# 질문
[구체적인 질문들]

# 출력 형식 지정
출력 형식: [JSON/마크다운/테이블]
```

---

## 템플릿 1: Phase 1 커밋 메시지 스코어링

```
# 역할
당신은 Git 히스토리를 분석하여 버그 관련 커밋을 찾는 전문가입니다.

# 컨텍스트
프로젝트: [프로젝트명]
문제: [증상 및 에러 메시지]
목표: 40개 커밋 중 문제와 관련된 커밋을 찾아 우선순위 부여

# 데이터
다음은 최근 40개 커밋 메시지입니다:

| 해시 | 날짜 | 작성자 | 메시지 |
|------|------|--------|--------|
| abc1 | 2024-02-01 | dev1 | feat: add OAuth login |
| def2 | 2024-02-02 | dev2 | fix: session bug |
| ghi3 | 2024-02-03 | dev1 | docs: update README |
...

# 분류 기준
- 10점: 문제와 직접 관련 (해당 모듈/함수 수정)
  예: "fix: login session token missing" (문제가 세션 토큰이면 10점)
  
- 7-9점: 간접 관련 (의존 모듈 변경)
  예: "refactor: auth middleware" (로그인 시스템 사용하므로 8점)
  
- 4-6점: 잠재적 관련 (공통 리소스 접근)
  예: "chore: update Redis client" (세션이 Redis 사용하므로 5점)
  
- 1-3점: 관련 가능성 낮음
  예: "feat: add dark mode" (UI 변경이므로 2점)
  
- 0점: 완전 무관
  예: "docs: fix typo" (문서만 수정이므로 0점)

# 질문
각 커밋을 0-10점으로 스코어링하고 근거를 제시하세요.

# 출력 형식
마크다운 테이블로 출력하되, 점수 내림차순 정렬:

| 점수 | 해시 | 메시지 | 분류 근거 |
|------|------|--------|-----------|
| 10   | def2 | fix: session bug | "session" 키워드 직접 일치, 문제 영역 정확 |
| 8    | abc1 | feat: add OAuth login | 로그인 시스템 변경, 간접 영향 가능 |
...

HIGH 우선순위 (9-10점) 커밋만 별도로 요약:
- def2: fix: session bug
- [다른 HIGH 커밋들...]
```

---

## 템플릿 2: Phase 2 Good/Bad Case 분석

```
# 역할
당신은 코드 변경 이력을 분석하여 버그의 정확한 원인을 찾는 전문가입니다.

# 컨텍스트
문제: [구체적 증상]
목표: Good Case (정상 작동)와 Bad Case (문제 발생)를 식별하고 핵심 델타 분석

# 데이터
다음은 HIGH 우선순위 커밋들의 상세 diff입니다:

=== 커밋 abc123 (2일 전) ===
```diff
--- a/login.js
+++ b/login.js
@@ -10,6 +10,7 @@
 function login(credentials) {
   const user = authenticate(credentials);
   const token = generateToken(user);
+  session.save(token);  // 추가됨
   return token;
 }
```

=== 커밋 def456 (1일 전) ===
```diff
--- a/login.js
+++ b/login.js
@@ -10,7 +10,6 @@
 function login(credentials) {
   const user = authenticate(credentials);
-  const token = generateToken(user);
-  session.save(token);  // 삭제됨
+  const authToken = generateToken(user);  // 리네이밍
   return authToken;
 }
```

# 질문

## Q1: Good Case 식별
어느 커밋이 정상 작동했나요? (근거 포함)

## Q2: Bad Case 식별
어느 커밋부터 문제가 발생했나요?

## Q3: 핵심 델타 (Δ)
Good → Bad 전환의 정확한 변경점은 무엇인가요?

## Q4: 핵심 메커니즘 (수도코드)
Good Case의 핵심 메커니즘을 수도코드로 표현하세요:
```
function core_mechanism():
    step1
    step2  # ← 핵심
    step3
```

## Q5: 제약 조건
Good Case가 만족하는 제약 조건은?
예: "CONSTRAINT-001: 토큰 생성 후 반드시 저장"

## Q6: 위반 사항
Bad Case가 위반한 제약 조건은?

# 출력 형식

### Good Case
- **커밋:** abc123
- **핵심 메커니즘:**
  ```python
  token = generate()
  session.save(token)  # ← 핵심!
  return token
  ```
- **제약 조건:**
  - CONSTRAINT-001: 토큰 생성 후 세션 저장 필수
  - CONSTRAINT-002: 저장 실패 시 예외 발생

### Bad Case
- **커밋:** def456
- **델타:** `session.save(token)` 호출 삭제됨
- **위반:** CONSTRAINT-001

### 근본 원인
리네이밍 과정에서 session.save() 라인이 의도치 않게 삭제됨
```

---

## 템플릿 3: Phase 5 악순환 패턴 분석

```
# 역할
당신은 소프트웨어 개발 패턴을 분석하여 반복되는 문제를 찾는 전문가입니다.

# 컨텍스트
기간: 최근 3개월
대상: authentication 모듈
목표: 악순환 패턴 탐지 및 근본 원인 분석

# 데이터
다음은 authentication 관련 커밋 타임라인입니다:

| 주차 | 커밋 타입 | 메시지 | 간격 |
|------|----------|--------|------|
| Week 1 | feat | OAuth 로그인 추가 | - |
| Week 2 | fix | 세션 버그 수정 | +7일 |
| Week 3 | revert | OAuth 롤백 | +7일 (fix 후 7일) |
| Week 4 | fix | 세션 재수정 | +7일 |
| Week 5 | refactor | 인증 전면 리팩토링 | +7일 |
| Week 6 | fix | 또 세션 버그 | +7일 |
| Week 7 | fix | 세션 타임아웃 문제 | +7일 |

# 추가 데이터

## 파일 수정 빈도
```bash
$ git log --follow -- auth/session.js | wc -l
23  # 3개월 동안 23회 수정
```

## Fix → Revert 패턴
```
fix (Week 2) → revert (Week 3): 7일 간격
fix (Week 4) → (문제 지속)
fix (Week 6) → fix (Week 7): 7일 간격 (재발)
```

# 질문

## Q1: 악순환 패턴 식별
반복되는 패턴이 보이나요? 구체적으로 설명하세요.

## Q2: 근본 원인 가설
이러한 패턴의 근본 원인은 무엇일까요? 3가지 가설 제시:
- 기술적 원인 (설계 결함, 기술 부채)
- 프로세스 원인 (테스트 부족, 리뷰 미흡)
- 지식 원인 (도메인 이해 부족, 문서화 미흡)

## Q3: 신호 분석
어떤 조기 경고 신호가 있었나요?
예: "Week 2 fix 후 1주일 만에 revert → 근본 원인 미해결 신호"

## Q4: 탈출 전략
이 악순환에서 벗어나기 위한 구체적 전략은?

# 출력 형식

### 악순환 패턴: [패턴 이름]

**증상:**
- [구체적 증상]
- 발생 빈도: [횟수/기간]

**패턴 분석:**
```
Week 1: 새 기능 → Week 2: 버그 → Week 3: 롤백
(반복 3회)
```

**근본 원인 가설:**
1. **기술적:** [가설 + 증거]
   신뢰도: [%]
   
2. **프로세스:** [가설 + 증거]
   신뢰도: [%]
   
3. **지식:** [가설 + 증거]
   신뢰도: [%]

**조기 경고 신호:**
- [신호 1]: [설명]
- [신호 2]: [설명]

**탈출 전략:**
1. 단기 (1주):
   - [ ] [구체적 행동]
   
2. 중기 (1개월):
   - [ ] [구체적 행동]
   
3. 장기 (3개월):
   - [ ] [구체적 행동]

**성공 지표:**
- [측정 가능한 지표 1]
- [측정 가능한 지표 2]
```

---

## 템플릿 4: 로직 오류 분석 (Phase 3-4)

```
# 역할
당신은 복잡한 로직 오류를 찾는 디버깅 전문가입니다.

# 컨텍스트
문제: [증상]
환경: [언어, 프레임워크]
시도한 방법: [문법 검증 ✅, Bisect ✅, Mutation Test ❌]

# 데이터

## 의심 코드
```python
async def process_payment(order_id):
    order = fetch_order(order_id)
    
    # 병렬 실행
    payment, inventory, notification = await asyncio.gather(
        charge_card(order.total),
        reserve_inventory(order.items),
        send_email(order.customer)
    )
    
    if payment.failed:
        # 롤백 시도
        await release_inventory(order.items)
        raise PaymentError()
    
    return payment
```

## 에러 로그
```
간헐적 발생 (30% 확률):
- "Inventory already released"
- "Payment succeeded but order marked as failed"
```

## 실행 추적
```
Run 1 (성공):
  t=0ms: charge_card 시작
  t=50ms: reserve_inventory 시작
  t=100ms: charge_card 완료
  t=150ms: reserve_inventory 완료
  
Run 2 (실패):
  t=0ms: charge_card 시작
  t=50ms: reserve_inventory 시작
  t=80ms: charge_card 실패!
  t=85ms: release_inventory 시작
  t=100ms: reserve_inventory 완료 (이미 release 시작됨!)
```

# 질문

## Q1: 문제 원인 분석
로그와 실행 추적을 보고 문제의 정확한 원인을 설명하세요.

## Q2: 레이스 컨디션 검증
이것이 레이스 컨디션인가요? 증거는?

## Q3: 재현 시나리오
어떤 타이밍에 문제가 발생하나요? 단계별 시나리오:
```
Step 1: [무엇이 먼저]
Step 2: [그 다음]
Step 3: [그래서 문제]
```

## Q4: 수정 방안
어떻게 고쳐야 하나요? (코드 포함)

## Q5: 검증 방법
수정 후 어떻게 확인하나요? (테스트 코드 포함)

# 출력 형식

### 문제 원인
[상세 설명]

### 레이스 컨디션 여부
✅ Yes / ❌ No
[증거]

### 재현 시나리오
```
1. charge_card()가 실패하여 payment.failed = True
2. 동시에 reserve_inventory()는 아직 실행 중
3. if payment.failed 조건 진입 → release_inventory() 시작
4. reserve_inventory() 완료 (이미 release 중!)
5. 충돌: "Inventory already released"
```

### 수정 방안
```python
async def process_payment(order_id):
    order = fetch_order(order_id)
    
    # 1단계: 결제만 먼저
    payment = await charge_card(order.total)
    
    if payment.failed:
        raise PaymentError()
    
    # 2단계: 결제 성공 후 나머지
    try:
        inventory, notification = await asyncio.gather(
            reserve_inventory(order.items),
            send_email(order.customer)
        )
    except Exception as e:
        # 롤백: 결제 취소
        await refund_card(payment.transaction_id)
        raise
    
    return payment
```

### 검증 방법
```python
@pytest.mark.repeat(100)  # 100회 반복
async def test_payment_no_race_condition():
    # 카드 결제 실패 시뮬레이션
    with mock.patch('charge_card', side_effect=PaymentError):
        with pytest.raises(PaymentError):
            await process_payment(123)
        
        # inventory 예약 시도 안 했는지 확인
        assert not inventory_reserved(123)
```
```

---

## 프롬프트 작성 팁

### 1. 구조화된 입력

❌ 나쁜 예:
```
이 커밋들 봐줘. 뭐가 문제야?
abc123, def456, ghi789
```

✅ 좋은 예:
```
다음 3개 커밋을 분석해주세요:

| 해시 | 메시지 | 변경 파일 |
|------|--------|-----------|
| abc123 | fix: session | login.js |
| def456 | refactor: auth | auth.js |
| ghi789 | feat: OAuth | oauth.js |

질문: 세션 토큰 누락 문제와 가장 관련된 커밋은?
```

### 2. 명확한 출력 형식

❌ 나쁜 예:
```
분석해줘
```

✅ 좋은 예:
```
출력 형식:
1. 원인: [한 문장 요약]
2. 증거: [코드 라인 또는 로그]
3. 해결책: [수정 코드]
```

### 3. Few-shot 예시 제공

```
# 예시 1 (참고용)
입력: "fix: login session missing"
출력: 점수 10 (session 키워드 직접 일치)

# 예시 2 (참고용)
입력: "docs: update README"
출력: 점수 0 (문서만 수정, 무관)

# 실제 분석 대상
입력: "refactor: authentication middleware"
출력: [당신이 분석]
```

### 4. 컨텍스트 제한

Gemini 컨텍스트가 크더라도 핵심만 제공:

```
❌ 전체 diff (10,000줄) 제공

✅ 변경된 함수만 (100줄) 제공
```

---

## 자주 하는 실수

### 실수 1: 모호한 질문
```
❌ "이거 왜 안 돼?"
✅ "login.js 45번 줄에서 session.save() 호출 시 null reference 에러 발생. 원인은?"
```

### 실수 2: 컨텍스트 부족
```
❌ "abc123 커밋 분석해줘"
✅ "abc123 커밋 분석해줘. 문제: 로그인 후 401 에러. 이전 커밋에선 정상 작동."
```

### 실수 3: 출력 형식 미지정
```
❌ "분석해줘"
✅ "JSON 형식으로 출력: {cause: '', fix: '', confidence: 0-100}"
```

---

## 결론

**좋은 프롬프트 = 좋은 결과**

체크리스트:
- [ ] 역할 명확히 정의
- [ ] 컨텍스트 충분히 제공
- [ ] 데이터 구조화
- [ ] 질문 구체적
- [ ] 출력 형식 지정
- [ ] Few-shot 예시 (선택)
