"""LLM 프로바이더 레지스트리 — 이름으로 프로바이더 인스턴스를 조회한다."""

from src.core.llm_base import LLMProvider

_PROVIDERS: dict[str, type[LLMProvider]] = {}


def register(name: str, cls: type[LLMProvider]) -> None:
    """프로바이더 클래스를 이름으로 등록한다."""
    _PROVIDERS[name] = cls


def get_provider(name: str) -> LLMProvider:
    """등록된 프로바이더 인스턴스를 반환한다. 미등록 시 KeyError."""
    if name not in _PROVIDERS:
        raise KeyError(f"미등록 LLM 프로바이더: '{name}'")
    return _PROVIDERS[name]()
