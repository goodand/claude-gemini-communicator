# Troubleshooting — async-migration-verify

## CASE-001: Dead import survived a green async migration

**증상**: async 전환 후 `tests pass` 였지만 이전 sync import가 그대로 남아 있었다.
**원인**: migration review가 runtime path만 보고 import residue를 보지 않았다.
**해결**: dead import scan을 checkpoint 1로 고정했다.
**교훈**: green tests는 unused residue를 닫지 않는다.

## CASE-002: Concurrency guard solved race but created silent UX loss

**증상**: in-flight guard가 두 번째 요청을 조용히 드롭했다.
**원인**: technical guard만 추가하고 visible feedback을 추가하지 않았다.
**해결**: status message / disabled action / busy UX를 checkpoint 3에 넣었다.
**교훈**: async migration은 race fix와 UX semantics를 같이 봐야 한다.
