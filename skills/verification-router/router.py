#!/usr/bin/env python3
"""Verification Router — 검증 패밀리 skill 라우터.

이 PC의 skill 코퍼스에서 1등 주제는 "검증"(verify/validate가 skill의 절반에
등장, Claim Verifier가 최다 사용). 검증 계열 skill들이 개별로 흩어져 있어,
검증 의도(intent)를 받아 알맞은 skill 패밀리로 라우팅한다.

메커니즘은 Hermes toolsets.py 패턴을 차용:
  - FAMILIES 레지스트리: {name: {description, skills, includes}}
  - resolve(name): includes를 재귀 합성 + 사이클 감지 + dedup
  - route(intent): 자연어 의도 → 키워드 규칙 → 패밀리
실제 skill 경로 존재 확인은 형제 모듈 resolve_skill.py에 위임한다.

CLI:
    python3 router.py families                 # 패밀리 목록
    python3 router.py resolve merge-audit      # 패밀리 → 실제 skill 평탄화
    python3 router.py route "이 PR 머지해도 되나 검증"   # 의도 → 패밀리+skill
    python3 router.py hook                      # PreToolUse JSON(stdin) → 라우팅 힌트(stdout)

stdlib만. Claude/Codex/Gemini 공용.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS_DIR = HERE.parent  # <repo>/skills

# ── 검증 패밀리 레지스트리 (Hermes toolsets 패턴) ────────────────────
# claim-verifier가 허브. 나머지는 계층으로 include 합성.
FAMILIES = {
    "claim": {
        "description": "핵심 주장/사실 검증 허브 (proof-carrying claim 검증)",
        "skills": ["claim-verifier"],
        "includes": [],
    },
    "evidence": {
        "description": "증거 수집·추적·감사 (OCR/이미지/실행 증거를 근거로)",
        "skills": ["evidence-trace-auditor", "evidence-to-knowledge-promoter",
                   "macos-ocr-evidence", "component-split-ocr-review",
                   "image-result-auditor"],
        "includes": ["claim"],
    },
    "consistency": {
        "description": "코드↔문서↔의존성 구조 정합성 검증",
        "skills": ["doc-code-sync-checker", "codebase-doc-alignment",
                   "depsolve-analyzer", "class-hierarchy-classifier"],
        "includes": ["claim"],
    },
    "decision-gate": {
        "description": "여러 findings를 하나의 통과/차단 판정으로 수렴",
        "skills": ["verification-decision-gate", "red-team-merge-verdict"],
        "includes": ["claim"],
    },
    "merge-audit": {
        "description": "브랜치/PR 머지 안전성 감사 (artifact/ci/docs/delete/runtime/ios)",
        "skills": ["artifact-noise-merge-audit", "ci-docs-merge-audit",
                   "delete-report-merge-audit", "native-ios-merge-audit",
                   "runtime-core-merge-audit"],
        "includes": ["evidence", "decision-gate"],
    },
    "semantic": {
        "description": "의미 모호성 제거·개념 명료성 검증",
        "skills": ["semantic-clarity-enhanced"],
        "includes": ["claim"],
    },
    "runtime-truth": {
        "description": "실행/런타임 상태의 실측 진위 확인 (simulator·async 등)",
        "skills": ["simctl-screenshot-state-check", "simctl-recording-finalization",
                   "ios-runtime-tail-recovery", "async-migration-verify"],
        "includes": ["evidence"],
    },
    "validation-run": {
        "description": "산출물 검증 실행 (caption/pptx/table 등 파이프라인 검증)",
        "skills": ["openai-image-caption-validation", "pptx-slide-screenshot-capture",
                   "table-branch-activation-slice"],
        "includes": ["evidence"],
    },
    "skill-eval": {
        "description": "agent skill 자체의 실행을 평가·측정 (behavior eval·benchmark·baseline diff)",
        "skills": ["measurement-evaluation-orchestrator", "agent-tool-benchmark",
                   "baseline-diff-lab", "skill-workflow-bridge-eval",
                   "slice-experiment-lab"],
        "includes": ["evidence"],
    },
    "all": {
        "description": "전체 검증 패밀리",
        "skills": [],
        "includes": ["merge-audit", "consistency", "semantic",
                     "runtime-truth", "validation-run", "skill-eval"],
    },
}

# ── 의도 → 패밀리 라우팅 규칙 (위에서부터 첫 매치) ───────────────────
ROUTE_RULES = [
    (r"skill.*(평가|측정|eval|benchmark|behavior|behaviour)|(평가|측정|benchmark).*skill|"
     r"baseline.?diff|with.?without|autorat|rater|스킬.*평가", "skill-eval"),
    (r"merge|머지|병합|\bpr\b|풀리퀘|pull request", "merge-audit"),
    (r"문서|doc|readme|sync|정합|align|일관", "consistency"),
    (r"의존|dependenc|circular|phantom|순환", "consistency"),
    (r"모호|명료|semantic|의미|ambig|monosem", "semantic"),
    (r"simulat|simctl|런타임|runtime state|시뮬|async|비동기", "runtime-truth"),
    (r"ocr|caption|이미지|image|스크린샷|screenshot|pptx|table", "validation-run"),
    (r"증거|evidence|trace|추적|감사|audit", "evidence"),
    (r"판정|verdict|gate|통과|차단|decision", "decision-gate"),
    (r"주장|claim|사실|fact|검증|verif|validat|proof", "claim"),
]


def resolve(name, visited=None):
    """패밀리를 실제 skill 이름 리스트로 평탄화 (includes 재귀, 사이클 감지, dedup)."""
    if visited is None:
        visited = set()
    if name in visited or name not in FAMILIES:
        return []
    visited.add(name)
    fam = FAMILIES[name]
    out = list(fam["skills"])
    for inc in fam["includes"]:
        out.extend(resolve(inc, visited.copy()))
    seen, dedup = set(), []
    for s in out:
        if s not in seen:
            seen.add(s); dedup.append(s)
    return dedup


def _load_resolver():
    """형제 resolve_skill.py를 import (skill 실제 경로 확인용)."""
    try:
        sys.path.insert(0, str(SKILLS_DIR))
        import resolve_skill  # type: ignore
        return resolve_skill
    except Exception:
        return None


def _existing(skills):
    """resolve_skill로 실제 존재하는 skill만 (name -> path 또는 None)."""
    rs = _load_resolver()
    if not rs:
        return {s: None for s in skills}
    winners, _ = rs.discover()
    return {s: (winners[s]["path"] if s in winners else None) for s in skills}


def route(intent):
    text = (intent or "").lower()
    for pat, fam in ROUTE_RULES:
        if re.search(pat, text):
            return fam
    return "claim"  # 기본: 검증 허브


def cmd_families(_args):
    for name, fam in FAMILIES.items():
        inc = f" (includes: {', '.join(fam['includes'])})" if fam["includes"] else ""
        print(f"{name:<16} {fam['description']}{inc}")
    return 0


def cmd_resolve(args):
    fam = args[0] if args else "all"
    if fam not in FAMILIES:
        print(f"unknown family: {fam}", file=sys.stderr); return 1
    skills = resolve(fam)
    ex = _existing(skills)
    for s in skills:
        mark = ex[s] if ex[s] else "(MISSING)"
        print(f"{s:<36} {mark}")
    print(f"\n{fam}: {len(skills)} skills, "
          f"{sum(1 for v in ex.values() if v)} present")
    return 0


def cmd_route(args):
    intent = " ".join(args)
    fam = route(intent)
    skills = resolve(fam)
    ex = _existing(skills)
    out = {"intent": intent, "family": fam,
           "description": FAMILIES[fam]["description"],
           "skills": [{"name": s, "path": ex[s], "present": bool(ex[s])}
                      for s in skills]}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_hook(_args):
    """PreToolUse 스타일 JSON(stdin)을 읽어 검증 라우팅 힌트를 emit.

    prompt/tool_input/description 등에서 검증 의도가 보이면 추천 패밀리+skill을
    additionalContext로 돌려준다. 검증 의도가 없으면 빈 통과.
    """
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return 0
    blob = json.dumps(payload, ensure_ascii=False).lower()
    if not re.search(r"검증|verif|validat|audit|머지|merge|정합|모호|claim|proof", blob):
        print(json.dumps({})); return 0
    fam = route(blob)
    skills = [s for s in resolve(fam)]
    ctx = (f"[verification-router] 검증 의도 감지 → 추천 패밀리 '{fam}': "
           + ", ".join(skills[:6]))
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": ctx,
        }
    }, ensure_ascii=False))
    return 0


def main(argv):
    if not argv:
        return cmd_families(argv)
    cmd, rest = argv[0], argv[1:]
    table = {"families": cmd_families, "resolve": cmd_resolve,
             "route": cmd_route, "hook": cmd_hook}
    if cmd not in table:
        print(f"usage: router.py [families|resolve <fam>|route <intent>|hook]",
              file=sys.stderr)
        return 2
    return table[cmd](rest)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
