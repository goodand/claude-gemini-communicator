# Good/Bad Case 패턴 라이브러리

해결된 이슈들을 패턴화하여 저장하는 라이브러리입니다. 새로운 문제 발생 시 이 라이브러리를 먼저 검색하세요.

## 패턴 형식

```json
{
  "pattern_id": "UNIQUE_ID",
  "category": "authentication | database | async | ui | etc",
  "good_commit": "커밋 해시",
  "mechanism": "핵심 메커니즘 (수도코드)",
  "constraints": ["제약 조건 리스트"],
  "bad_commit": "커밋 해시",
  "violation": "위반한 제약 조건",
  "symptom": "증상",
  "root_cause": "근본 원인",
  "auto_check": "자동 검증 방법 (linter 등)"
}
```

---

## 저장된 패턴들

### PATTERN-001: SESSION_SAVE_MISSING

**카테고리:** authentication

**Good Case (커밋 abc123):**
```python
def login(credentials):
    user = authenticate(credentials)
    token = generate_token(user)
    session.save(token)  # ← 핵심!
    return token
```

**핵심 메커니즘:**
```
token = generate_token(user)
session.save(token)  # 생성 후 즉시 저장
return token
```

**제약 조건:**
- CONSTRAINT-001: 토큰 생성 후 반드시 세션 저장
- CONSTRAINT-002: 저장 실패 시 예외 발생하여 롤백

**Bad Case (커밋 def456):**
```python
def login(credentials):
    user = authenticate(credentials)
    token = generate_token(user)
    # session.save(token)  # ← 누락!
    return token
```

**위반 내용:** CONSTRAINT-001

**증상:**
- 로그인 성공하지만 후속 인증 필요 페이지에서 401 Unauthorized
- 세션 쿠키는 설정되지만 서버에 세션 데이터 없음

**근본 원인:**
- 리팩토링 중 `sessionToken` → `authToken` 리네이밍
- 리네이밍 과정에서 `session.save()` 호출 라인 삭제됨

**자동 검증 방법:**
```javascript
// ESLint 규칙
module.exports = {
  rules: {
    'require-session-save': {
      create(context) {
        return {
          CallExpression(node) {
            if (node.callee.name === 'generateToken') {
              // 다음 3줄 이내에 session.save() 있는지 확인
              const nextLines = getNextLines(node, 3);
              if (!nextLines.includes('session.save')) {
                context.report({
                  node,
                  message: 'Token 생성 후 session.save() 누락'
                });
              }
            }
          }
        };
      }
    }
  }
};
```

**재발 방지:**
- [ ] ESLint 규칙 추가
- [ ] 통합 테스트: 로그인 후 세션 존재 확인
- [ ] Code Review 체크리스트에 추가

---

### PATTERN-002: ASYNC_RACE_CONDITION

**카테고리:** async

**Good Case (커밋 ghi789):**
```javascript
async function loadUserData(userId) {
  const user = await fetchUser(userId);
  const preferences = await fetchPreferences(userId);
  const settings = await fetchSettings(userId);
  
  return { user, preferences, settings };
}
```

**핵심 메커니즘:**
```
data1 = await fetch1()  # 순차 실행
data2 = await fetch2()
data3 = await fetch3()
return merge(data1, data2, data3)
```

**제약 조건:**
- CONSTRAINT-003: 의존성 있는 비동기 호출은 순차 실행
- CONSTRAINT-004: 병렬 실행 시 Promise.all 사용

**Bad Case (커밋 jkl012):**
```javascript
async function loadUserData(userId) {
  // 병렬 실행으로 "최적화"
  const [user, preferences, settings] = await Promise.all([
    fetchUser(userId),
    fetchPreferences(userId),  // user.id 필요한데 user 아직 안 옴
    fetchSettings(userId)
  ]);
  
  return { user, preferences, settings };
}
```

**위반 내용:** CONSTRAINT-003

**증상:**
- 간헐적으로 preferences가 빈 객체로 로드됨
- 재현율 약 30% (네트워크 속도 의존)

**근본 원인:**
- `fetchPreferences()`가 내부적으로 `user.email`을 사용
- Promise.all로 병렬 실행 시 user가 아직 로드 안 됨

**자동 검증 방법:**
```javascript
// 통합 테스트
test('loadUserData should return complete data', async () => {
  for (let i = 0; i < 100; i++) {  // 100회 반복
    const data = await loadUserData(123);
    expect(data.preferences).not.toEqual({});
    expect(data.preferences.email).toBeDefined();
  }
});
```

**재발 방지:**
- [ ] 의존성 그래프 문서화
- [ ] 병렬 실행 전 의존성 검토 필수
- [ ] Intermittent 테스트 100회 실행

---

### PATTERN-003: NULL_CHECK_MISSING

**카테고리:** defensive-programming

**Good Case (커밋 mno345):**
```python
def process_order(order_id):
    order = get_order(order_id)
    if order is None:
        raise OrderNotFoundError(f"Order {order_id} not found")
    
    if order.status != 'pending':
        raise InvalidOrderStateError(f"Order {order_id} is {order.status}")
    
    process(order)
```

**핵심 메커니즘:**
```
data = fetch()
if data is None:
    raise NotFoundError
if not validate(data):
    raise ValidationError
process(data)
```

**제약 조건:**
- CONSTRAINT-005: 외부 데이터는 항상 null 체크
- CONSTRAINT-006: 비즈니스 로직 전 상태 검증

**Bad Case (커밋 pqr678):**
```python
def process_order(order_id):
    order = get_order(order_id)
    # null 체크 없음!
    process(order)  # order가 None이면 AttributeError
```

**위반 내용:** CONSTRAINT-005, CONSTRAINT-006

**증상:**
```
AttributeError: 'NoneType' object has no attribute 'status'
  File "orders.py", line 45, in process_order
    process(order)
```

**근본 원인:**
- "항상 존재한다"는 가정
- Edge Case (삭제된 주문) 미고려

**자동 검증 방법:**
```python
# mypy strict mode
from typing import Optional

def get_order(order_id: int) -> Optional[Order]:
    """주문 조회 (없으면 None 반환)"""
    ...

def process_order(order_id: int) -> None:
    order = get_order(order_id)
    # mypy error: Value of type "Optional[Order]" is not indexable
    process(order)  # ← 여기서 에러 (null 체크 안 함)
```

**재발 방지:**
- [ ] mypy strict mode 활성화
- [ ] Code Review: 모든 Optional 타입 체크
- [ ] 테스트: Edge Case (null, 빈 배열 등) 필수

---

### PATTERN-004: TIMEZONE_MISMATCH

**카테고리:** datetime

**Good Case (커밋 stu901):**
```python
from datetime import datetime, timezone

def create_event(title, start_time_utc):
    # 모든 시간은 UTC로 저장
    event = Event(
        title=title,
        start_time=start_time_utc.replace(tzinfo=timezone.utc)
    )
    db.save(event)
```

**핵심 메커니즘:**
```
# 입력: UTC
# 저장: UTC
# 출력: UTC (클라이언트가 로컬 변환)
all_times_in_utc()
```

**제약 조건:**
- CONSTRAINT-007: 모든 시간은 UTC로 저장
- CONSTRAINT-008: 로컬 시간 변환은 클라이언트 책임

**Bad Case (커밋 vwx234):**
```python
def create_event(title, start_time):
    # 시간대 정보 없음 (naive datetime)
    event = Event(
        title=title,
        start_time=start_time  # ← 위험!
    )
    db.save(event)
```

**위반 내용:** CONSTRAINT-007

**증상:**
- 서울에서 생성한 이벤트가 뉴욕에서 9시간 일찍 표시됨
- DST 전환 시 1시간 오차 발생

**근본 원인:**
- Naive datetime 사용 (시간대 정보 없음)
- 서버 로컬 시간 가정

**자동 검증 방법:**
```python
# pytest
def test_event_times_are_utc():
    event = create_event("Meeting", datetime(2024, 1, 1, 10, 0))
    
    # 시간대 정보 있는지 확인
    assert event.start_time.tzinfo is not None
    
    # UTC인지 확인
    assert event.start_time.tzinfo == timezone.utc
```

**재발 방지:**
- [ ] Linter: naive datetime 경고
- [ ] DB 스키마: TIMESTAMP WITH TIME ZONE
- [ ] 테스트: 다양한 시간대 검증

---

## 패턴 검색 방법

### 1. 증상으로 검색

```bash
grep -r "401 Unauthorized" PATTERN_LIBRARY.md
# → PATTERN-001: SESSION_SAVE_MISSING
```

### 2. 카테고리로 검색

```bash
grep "\"category\": \"authentication\"" PATTERN_LIBRARY.md
# → PATTERN-001, PATTERN-006, ...
```

### 3. 자동 매칭 스크립트

```python
def find_similar_patterns(symptom, error_message):
    """증상과 에러 메시지로 유사 패턴 검색"""
    
    patterns = load_pattern_library()
    
    matches = []
    for pattern in patterns:
        # 키워드 매칭
        if symptom in pattern['symptom']:
            matches.append((pattern, 0.9))
        
        # 에러 메시지 유사도
        similarity = calculate_similarity(error_message, pattern['symptom'])
        if similarity > 0.7:
            matches.append((pattern, similarity))
    
    return sorted(matches, key=lambda x: x[1], reverse=True)

# 사용 예시
similar = find_similar_patterns(
    symptom="로그인 후 인증 실패",
    error_message="401 Unauthorized"
)

for pattern, score in similar[:3]:
    print(f"{pattern['pattern_id']}: {score:.0%} 유사")
    # PATTERN-001: 90% 유사
```

---

## 새 패턴 추가 방법

1. 문제 해결 완료
2. `scripts/pattern_archiver.py` 실행
3. 메타데이터 입력 (대화형)
4. 자동으로 PATTERN_LIBRARY.md에 추가

```bash
python scripts/pattern_archiver.py \
  --good abc123 \
  --bad def456 \
  --category authentication \
  --interactive
```

---

## 사용 원칙

1. 새 문제 → 먼저 라이브러리 검색
2. 유사 패턴 → 해결책 참고
3. 새 패턴 → `scripts/pattern_archiver.py`로 추가
4. 재발 → 패턴 강화
