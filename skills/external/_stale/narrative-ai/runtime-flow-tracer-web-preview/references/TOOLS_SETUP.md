# Tools Setup Guide

## Python: pyftrace

### 설치
```bash
pip install pyftrace
```

### 직접 사용
```bash
# 기본 추적
pyftrace my_script.py

# 상세 리포트
pyftrace --report my_script.py

# TUI 모드 (인터랙티브)
pyftrace tui my_script.py

# 표준 라이브러리 제외
pyftrace --no-stdlib my_script.py
```

### tracer.py와 함께 사용
```bash
python tracer.py python my_script.py
python tracer.py python my_script.py --args "input.txt"
```

---

## JavaScript: njstrace

### 설치
```bash
npm install -g njstrace
```

### 사용법

njstrace는 코드에 직접 삽입이 필요합니다:

```javascript
// app.js 상단에 추가
const njstrace = require('njstrace').inject({
    files: ['**/*.js'],
    wrapFunctions: true,
    formatter: {
        onEntry: function(log) {
            console.log('ENTER:', log.name);
        },
        onExit: function(log) {
            console.log('EXIT:', log.name, 'time:', log.span, 'ms');
        }
    }
});

// ... 기존 코드 ...
```

### 자동화 (계획)
향후 tracer.py가 자동으로 코드 인스트루먼테이션을 수행할 예정.

---

## JavaScript 대안: Jalangi2

학술 연구용 동적 분석 프레임워크.

### 설치
```bash
git clone https://github.com/nicknicknicknick/nicknick/nicknick.git
cd jalangi2
npm install
```

### 사용법
```bash
# 코드 변환
node src/js/commands/instrument.js --inlineIID --inlineSource app.js

# 분석 실행
node src/js/commands/direct.js --analysis src/js/analyses/callTracer.js app_jalangi_.js
```

---

## 대안 도구들

### Python

| 도구 | 특징 | 설치 |
|------|------|------|
| **pyftrace** (권장) | TUI, 리포트, 쉬운 사용 | `pip install pyftrace` |
| pycallgraph2 | Graphviz 출력 | `pip install pycallgraph2` |
| hunter | 디버깅 특화 | `pip install hunter` |
| viztracer | 플레임그래프 | `pip install viztracer` |

### JavaScript

| 도구 | 특징 | 설치 |
|------|------|------|
| **njstrace** | 간단한 인스트루먼테이션 | `npm i -g njstrace` |
| Jalangi2 | 학술용, 상세 분석 | Git clone |
| Iroh | 런타임 훅 | `npm i iroh` |

---

## 트러블슈팅

### pyftrace가 설치되지 않음
```bash
# Python 3.8+ 필요
python --version

# pip 업그레이드
pip install --upgrade pip

# 설치
pip install pyftrace
```

### pyftrace 출력이 비어있음
```bash
# 스크립트가 실제로 실행되는지 확인
python my_script.py

# 표준 라이브러리 포함해서 추적
pyftrace my_script.py  # --no-stdlib 없이
```

### njstrace가 작동하지 않음
```bash
# Node.js 버전 확인 (12+ 필요)
node --version

# 전역 설치 확인
npm list -g njstrace

# 로컬 설치 시도
npm install njstrace
```

---

## 참고 자료

- [pyftrace GitHub](https://github.com/kangtegong/pyftrace)
- [njstrace GitHub](https://github.com/nicknicknicknick/nicknick)
- [Jalangi2 GitHub](https://github.com/nicknicknicknick/nicknick)
