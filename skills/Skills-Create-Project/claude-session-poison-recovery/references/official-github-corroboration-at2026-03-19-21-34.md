# Official GitHub Corroboration

- source: `anthropics/claude-code` official GitHub issues
- purpose: `claude-session-poison-recovery`의 local troubleshooting takeaways 중 공식 GitHub로 직접 corroborate되는 부분과 아닌 부분을 분리한다

## Officially corroborated

- [Issue #1709](https://github.com/anthropics/claude-code/issues/1709)
  - `The request body is not valid JSON: no low surrogate in string`가 session 단위로 반복되고, `continue`가 같은 에러를 되풀이할 수 있다는 점을 직접 보여준다.
- [Issue #1832](https://github.com/anthropics/claude-code/issues/1832)
  - 같은 low-surrogate 400이 `continue`와 `/compact` 둘 다 막을 수 있음을 보여준다.
  - 공식 repo에서 `#1709` duplicate로 연결돼 있다.
- [Issue #3995](https://github.com/anthropics/claude-code/issues/3995)
  - 같은 low-surrogate 400이 다른 환경과 버전에서도 반복된다는 점을 보강한다.
- [Issue #9561](https://github.com/anthropics/claude-code/issues/9561)
  - VS Code extension에 file/selection context라는 기능 축이 실제로 존재한다는 점을 corroborate한다.
  - issue 본문에서 `ide_selection tags`와 selection context regression을 직접 언급한다.

## What remains local-only

- `Selected N lines from ... in Visual Studio Code`라는 정확한 배너 문자열
  - 이 문구 자체는 현재 local symptom evidence다.
  - 공식 GitHub issue에서는 selection context 존재는 corroborate되지만, 동일한 배너 문자열까지는 직접 확인되지 않는다.
- exact settings key such as `includeIdeSelection`
  - 공식 repo issue 기준으로는 exact key를 확인하지 못했다.
  - 따라서 이 key는 runtime/version-dependent local hint로만 취급해야 한다.
- `stored session corruption` vs `live context injection`의 우선순위 분기
  - 이 분기 자체는 local troubleshooting procedure다.
  - 공식 issue는 symptom corroboration을 제공하지만, canonical recovery order를 직접 정의해주지는 않는다.

## Practical reading rule

- official GitHub는 symptom existence를 corroborate하는 데 쓴다
- local KB와 runbook은 recovery order와 safety rule을 결정하는 데 쓴다
- 공식 issue로 확인되지 않은 key, banner, workaround는 `verified runtime only` 또는 `local-only signal`로 명시한다
