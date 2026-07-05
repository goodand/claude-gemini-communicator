# API Reference

depsolve-analyzer의 출력 형식 상세 명세.

## JSON 출력 구조

### AnalysisResult

```json
{
  "project_path": "/path/to/project",
  "ecosystem": "npm",
  "issues": [...],
  "summary": {...},
  "mermaid_diagram": "graph TD\n..."
}
```

### Issue 객체

```json
{
  "id": "a1b2c3d4",
  "type": "phantom|circular|diamond|multi_version",
  "severity": "critical|high|medium|low",
  "title": "Phantom dependency: axios",
  "locations": [
    "axios (src/api.ts:3)"
  ],
  "evidence": {
    "type": "phantom",
    "data": {
      "package": "axios",
      "ecosystem": "javascript",
      "import_count": 5,
      "files": ["src/api.ts", "src/client.ts"]
    },
    "visualization": null
  },
  "suggestion": "Add 'axios' to dependencies in package.json"
}
```

### Summary 객체

```json
{
  "total_packages": 45,
  "total_dependencies": 120,
  "issues_by_severity": {
    "high": 2,
    "medium": 1
  },
  "issues_by_type": {
    "phantom": 2,
    "diamond": 1
  }
}
```

## Issue Types

### phantom

manifest에 없는 import 탐지.

```json
{
  "type": "phantom",
  "data": {
    "package": "lodash",
    "ecosystem": "javascript",
    "import_count": 3,
    "files": ["src/utils.ts"]
  }
}
```

### circular

순환 의존성 탐지.

```json
{
  "type": "cycle",
  "data": {
    "path": ["A", "B", "C", "A"],
    "length": 3
  },
  "visualization": "graph LR\n  A --> B --> C --> A"
}
```

### diamond

다이아몬드 의존성 탐지.

```json
{
  "type": "diamond",
  "data": {
    "top": "app",
    "left": "lib-a",
    "right": "lib-b", 
    "bottom": "shared",
    "left_version": "^1.0.0",
    "right_version": "^2.0.0",
    "has_conflict": true
  }
}
```

### multi_version

동일 패키지 다중 버전 설치.

```json
{
  "type": "multi_version",
  "data": {
    "package": "lodash",
    "versions": ["4.17.21", "4.17.15"],
    "paths": [["app", "lib-a", "lodash"], ["app", "lib-b", "lodash"]]
  }
}
```

## Severity 기준

| Level | 기준 | 예시 |
|:------|:-----|:-----|
| critical | 빌드/런타임 실패 가능 | - |
| high | 즉시 해결 필요 | phantom, circular |
| medium | 권장 해결 | diamond (충돌), multi_version |
| low | 선택적 개선 | diamond (충돌 없음) |

## Ecosystem 값

- `npm`, `javascript`: JS/TS 프로젝트
- `pip`, `python`: Python 프로젝트
- `go`: Go 프로젝트
- `cargo`, `rust`: Rust 프로젝트
- `npm+python`: 하이브리드 프로젝트

## Import Types

`imports` 명령어 출력에서 사용:

| Type | 설명 | 예시 |
|:-----|:-----|:-----|
| import | ES6 static import | `import x from 'pkg'` |
| require | CommonJS require | `require('pkg')` |
| dynamic_import | 동적 import | `import('pkg')` |
| type_import | TypeScript type-only | `import type { X }` |
| re_export | Re-export | `export * from 'pkg'` |
| from_import | Python from import | `from pkg import x` |

## File Context

import가 발견된 파일의 컨텍스트:

- `source`: 메인 소스 코드
- `test`: 테스트 파일
- `config`: 설정 파일 (vite.config.ts 등)
- `script`: 스크립트 (scripts/ 디렉토리)

## Override 시스템

`.depsolve/overrides.yaml` 구조:

```yaml
version: "1.0"
last_updated: "2025-01-15T10:00:00"

typo_corrections:
  - detected: "reqeusts"
    corrected: "requests"
    verified: true

package_aliases:
  - import_name: "cv2"
    package_name: "opencv-python"
    verified: true

internal_modules:
  - module: "generated"
    verified: true

ignore_rules:
  - pattern: "test_*"
    reason: "Test utilities"
```

## 종료 코드

| 코드 | 의미 |
|:-----|:-----|
| 0 | 성공, HIGH 이슈 없음 |
| 1 | HIGH/CRITICAL 이슈 발견 |
