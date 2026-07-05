# 가설 생성 및 검증 방법론

이 문서는 Troubleshooting-CoT의 Phase 3에서 사용하는 가설 생성 및 검증 전략을 상세히 설명합니다.

## 가설 생성 원칙

### 1. 증거 기반 가설

**좋은 가설:**
```
H1: session.save() 호출 누락으로 인해 세션 토큰이 저장되지 않음
근거: Git diff에서 session.save() 라인 삭제 확인
```

**나쁜 가설:**
```
H1: 서버가 이상해서 로그인이 안 됨
근거: 그냥 그런 것 같음
```

### 2. 검증 가능한 가설

각 가설은 명확한 검증 방법이 있어야 합니다.

```
H1: session.save() 복원 시 → 문제 해결
검증: git show abc123:login.js | grep "session.save" >> login.js && npm test

H2: authToken → sessionToken 되돌림 → 해결
검증: sed -i 's/authToken/sessionToken/g' login.js && npm test

H3: 의존성 버전 이슈
검증: npm install session@1.2.3 && npm test
```

### 3. 신뢰도 점수

각 가설에 신뢰도를 부여하여 우선순위 결정:

```
H1: session.save() 복원 (신뢰도: 95%)
  - Git diff에서 직접 확인
  - Good Case에 명확히 존재
  
H2: 리네이밍 되돌림 (신뢰도: 60%)
  - 간접적 영향 가능성
  
H3: 의존성 버전 (신뢰도: 20%)
  - package.json 변경 없었음
  - 낮은 개연성
```

## 검증 방법론

### Method 1: 자동 문법 검증 (신뢰도: 100%)

**적용 대상:** 문법 오류, 타입 오류

```bash
# Python
python -m py_compile file.py
pylint --errors-only file.py

# JavaScript
eslint file.js
npm run type-check

# TypeScript
tsc --noEmit
```

**장점:**
- 즉시 실행 (1초 이내)
- 확정적 결과
- 70%+ 문제 해결

**단점:**
- 로직 오류 미탐지
- 런타임 이슈 미탐지

---

### Method 2: Git Bisect 자동화 (신뢰도: 90-95%)

**적용 대상:** Good/Bad Case가 명확할 때

```bash
git bisect start HEAD abc123
git bisect run ./test_script.sh
```

**test_script.sh 작성 예시:**
```bash
#!/bin/bash
# Exit 0 = Good, Exit 1 = Bad

npm install --silent
npm test -- --testNamePattern="login" 2>&1 | grep -q "PASS"
exit $?
```

**장점:**
- 자동으로 정확한 Bad Commit 특정
- log₂(N) 시간 복잡도 (40개 → 5-6회 테스트)

**단점:**
- 테스트가 안정적이어야 함
- Intermittent bug에는 부적합

---

### Method 3: Mutation Testing (신뢰도: 85-90%)

**적용 대상:** "이 함수가 원인일까?" 질문

```python
def mutation_test(suspect_function):
    """함수를 무력화하여 인과관계 검증"""
    
    # 1. 원본 백업
    original_code = read_file(suspect_function.file)
    
    # 2. Mock으로 대체
    mock_code = f"""
def {suspect_function.name}(*args, **kwargs):
    # 항상 성공 반환
    return SUCCESS_VALUE
"""
    inject_code(suspect_function.file, mock_code)
    
    # 3. 테스트 실행
    result = run_tests()
    
    # 4. 복원
    write_file(suspect_function.file, original_code)
    
    # 5. 평가
    if result.passed:
        return f"✅ {suspect_function.name} 무력화 → 문제 해결 (원인 확정)"
    else:
        return f"❌ {suspect_function.name} 무관"
```

**예시:**
```python
# 의심 함수: validateSession()
# 무력화: return True

# 결과: 테스트 통과
# → validateSession()이 원인
```

**장점:**
- 인과관계 명확히 파악
- 복잡한 의존성 배제

**단점:**
- Mock이 현실적이어야 함
- 부작용 있는 함수 주의

---

### Method 4: 하드코딩 재구현 (신뢰도: 80-90%)

**적용 대상:** 핵심 메커니즘 검증

```python
# 목표: 핵심 메커니즘만 추출하여 의존성 없이 재구현

# 원본 (복잡)
def login(credentials):
    user = AuthService.authenticate(credentials)
    token = TokenGenerator.create(user, expires_in=3600)
    SessionManager.persist(token, storage='redis')
    logger.info(f"User {user.id} logged in")
    analytics.track('login', user.id)
    return token

# 최소 구현 (핵심만)
def minimal_login(creds):
    # 인증 → 하드코딩
    if creds == {'user': 'test', 'pw': '1234'}:
        user = {'id': 1}
    else:
        raise AuthError()
    
    # 토큰 생성 → 하드코딩
    token = f"TOKEN_{user['id']}_12345"
    
    # ★ 핵심 메커니즘: 토큰 생성 후 즉시 저장
    SESSION_STORE[token] = user  # ← 이것만 유지
    
    return token

# 테스트
minimal_login({'user': 'test', 'pw': '1234'})
assert 'TOKEN_1_12345' in SESSION_STORE  # ✅ 통과

# Bad Case 재현
def bad_minimal_login(creds):
    user = {'id': 1}
    token = f"TOKEN_{user['id']}_12345"
    # SESSION_STORE[token] = user  # ← 누락
    return token

bad_minimal_login({'user': 'test', 'pw': '1234'})
assert 'TOKEN_1_12345' in SESSION_STORE  # ❌ 실패 (문제 재현)
```

**검증 결과:**
- ✅ 최소 구현 작동 → 메커니즘 이해 정확
- ❌ 최소 구현 실패 → 제약 조건 놓침, 재분석 필요

**장점:**
- 의존성 제거하여 핵심 집중
- 교육적 (완전 이해 증명)

**단점:**
- 수동 작업 필요
- 시간 소요 (10-30분)

---

### Method 5: 반사실적 조건문 (Counterfactual)

**적용 대상:** "만약 X를 안 했다면?" 질문

```bash
# H1: "session.save() 제거가 원인이다"
# 반사실: "session.save()를 복원하면 해결된다"

git checkout bad_commit
git show good_commit:login.js | grep -A 2 "session.save" >> login.js
npm test

# 결과: PASS → H1 검증됨 (신뢰도: 95%)
```

**템플릿:**
```
IF (변경 X를 되돌린다면)
THEN (문제가 해결될 것이다)

검증:
1. X 되돌리기
2. 테스트 실행
3. 결과 평가
```

**예시:**
```
H1: Redis 연결 타임아웃 증가가 원인
IF (timeout을 5초 → 30초로 늘린다면)
THEN (간헐적 로그인 실패가 사라질 것이다)

검증:
sed -i 's/timeout: 5000/timeout: 30000/g' config.js
npm test (100회 반복)
성공률: 100% → H1 검증
```

---

## 가설 검증 우선순위

```
1순위: 자동 문법 검증 (1초, 신뢰도 100%)
  ↓ 문제 없으면
2순위: Git Bisect (1-2분, 신뢰도 90-95%)
  ↓ 특정 커밋 찾음
3순위: Mutation Testing (5-10분, 신뢰도 85-90%)
  ↓ 원인 함수 특정
4순위: 하드코딩 재구현 (10-30분, 신뢰도 80-90%)
  ↓ 메커니즘 검증
5순위: LLM 로직 분석 (최후, 신뢰도 60-80%)
```

## 복합 검증 전략

여러 방법을 조합하여 신뢰도 향상:

```python
def comprehensive_verification(hypothesis):
    results = []
    
    # Step 1: 문법 검증
    if not syntax_check_passed():
        return "문법 오류 발견 → 즉시 수정"
    
    # Step 2: Bisect로 Bad Commit 특정
    bad_commit = git_bisect()
    results.append(f"Bad commit: {bad_commit}")
    
    # Step 3: Diff 분석
    delta = analyze_diff(bad_commit)
    results.append(f"Delta: {delta}")
    
    # Step 4: Mutation Testing
    suspect_functions = extract_changed_functions(delta)
    for func in suspect_functions:
        mutation_result = mutation_test(func)
        results.append(mutation_result)
        if "원인 확정" in mutation_result:
            # Step 5: 하드코딩 재구현으로 재확인
            minimal_impl = hardcode_mechanism(func)
            if minimal_impl.works():
                return f"✅ 원인 확정: {func} (신뢰도: 95%)"
    
    # Step 6: LLM 분석 (모든 방법 실패 시)
    return llm_analyze(results)
```

## 가설 검증 체크리스트

모든 가설은 다음 기준을 만족해야 합니다:

- [ ] **구체적**: "뭔가 이상함" ❌ → "session.save() 누락" ✅
- [ ] **검증 가능**: 명확한 검증 방법 존재
- [ ] **신뢰도 점수**: 0-100% 부여
- [ ] **증거 기반**: Git diff, 로그, 스택 트레이스 등
- [ ] **반증 가능**: 틀릴 수도 있음을 인정
- [ ] **우선순위**: 신뢰도 높은 것부터 검증

## Intermittent Bug 처리

간헐적 버그는 특별한 전략 필요:

```bash
# 100회 반복 테스트
for i in {1..100}; do
  npm test -- login > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "실패: Run $i"
    git log -1 --oneline > failure_context_$i.txt
  fi
done

# 실패율 계산
failures=$(ls failure_context_*.txt | wc -l)
echo "실패율: $failures/100"

# 가설: "Redis 경쟁 조건"
# 검증: Mutex 추가 후 재테스트
```

## 정리

**핵심 원칙:**
1. 실행 > 분석
2. 확정적 > 추측적
3. 빠름 > 느림
4. 단순 > 복잡

**권장 순서:**
1. Linter 돌려보기 (1초)
2. Git bisect 돌려보기 (2분)
3. 의심 함수 격리 테스트 (10분)
4. 하드코딩 재구현 (30분)
5. LLM에게 물어보기 (최후)

**성공 기준:**
- 가설 신뢰도 > 90%
- 검증 재현율 100% (Intermittent 제외)
- 하드코딩 재구현 성공
