"""Router 레이어 — 메시지 라우팅 규칙 엔진.

메시지 타입/파일 확장자에 따라 대상 에이전트를 결정한다.
config.json의 routing_rules로 규칙을 정의하며, 미설정 시 기본값(gemini) 사용.
"""

# 기본 라우팅 규칙 (config에 routing_rules가 없을 때)
_DEFAULT_RULES = [
    {"match_type": "evaluation_request", "target": "gemini"},
    {"match_type": "error_analysis_request", "target": "gemini"},
    {"match_type": "code_review_request", "target": "gemini"},
    {"match_ext": [".py", ".js", ".ts"], "target": "gemini"},
    {"match_type": "*", "target": "gemini"},  # fallback
]


def resolve_target(message_type: str, config: dict,
                   file_path: str | None = None) -> str:
    """메시지 타입과 파일 경로에 따라 대상 에이전트를 결정한다.

    config['routing_rules']가 있으면 해당 규칙을 순회하고,
    없으면 기본 규칙(_DEFAULT_RULES)을 사용한다.
    """
    rules = config.get("routing_rules", _DEFAULT_RULES)

    for rule in rules:
        # 메시지 타입 매칭
        match_type = rule.get("match_type")
        if match_type and match_type != "*":
            if match_type != message_type:
                continue

        # 파일 확장자 매칭
        match_ext = rule.get("match_ext")
        if match_ext and file_path:
            if not any(file_path.endswith(ext) for ext in match_ext):
                continue
        elif match_ext and not file_path:
            continue  # 확장자 규칙인데 파일 경로 없으면 스킵

        return rule.get("target", "gemini")

    return "gemini"  # 최종 fallback


def list_available_targets(config: dict) -> list:
    """설정된 라우팅 규칙에서 사용 가능한 대상 에이전트 목록을 반환한다."""
    rules = config.get("routing_rules", _DEFAULT_RULES)
    targets = set()
    for rule in rules:
        target = rule.get("target")
        if target:
            targets.add(target)
    return sorted(targets)
