"""LLM 프로바이더 추상 인터페이스."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """LLM 프로바이더 추상 베이스 클래스."""

    @abstractmethod
    def call(self, content: str, prompt: str, config: dict,
             file_path: str | None = None) -> str:
        """동기 호출."""
        ...

    @abstractmethod
    def call_async(self, content: str, prompt: str, config: dict,
                   file_path: str | None = None,
                   source: str = "Async") -> str:
        """비동기 호출 (fire-and-forget)."""
        ...
