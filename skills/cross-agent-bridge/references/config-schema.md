# Config Schema (`config/config.json`)

## Core

- `gemini_cmd` (string): Gemini CLI 경로
- `gemini_timeout` (number): 호출 타임아웃(초)
- `watch_extensions` (array[string]): 감시 확장자
- `exclude_files` (array[string]): 제외 파일

## Prompt

- `evaluation_prompt` (string): 문서 리뷰 프롬프트
- `code_evaluation_prompt` (string): 코드 리뷰 프롬프트
- `code_extensions` (array[string]): 코드 확장자

## SDK

- `sdk.enabled` (bool)
- `sdk.model` (string)
- `sdk.fallback_models` (array[string])
- `sdk.fallback_to_cli` (bool)
- `sdk.api_key_env` (string)
- `sdk.max_output_tokens` (int)
- `sdk.temperature` (number, 0~2 권장)

## Runtime

- `async_mode` (bool)
- `a2a_schema_enabled` (bool)
- `error_detection.enabled` (bool)
- `error_detection.thresholds` (object: critical/high/medium/low >= 1)
