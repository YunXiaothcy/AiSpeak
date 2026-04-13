"""
Abstract base class for AI providers.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AIProviderType(Enum):
    """Supported AI provider types."""
    OPENAI = "openai"
    GROK = "grok"
    CLAUDE = "claude"
    QWEN = "qwen"


@dataclass
class AIRequestConfig:
    """Configuration for AI generation request."""
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4000
    stream: bool = True


@dataclass
class AIResponseChunk:
    """A single chunk from streaming response."""
    content: str
    is_final: bool = False
    metadata: dict = field(default_factory=dict)


class BaseAIProvider(ABC):
    """Abstract base for AI LLM providers."""
    
    provider_type: AIProviderType
    supported_models: list[str]
    
    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self._client = None
    
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        config: AIRequestConfig = None,
    ) -> str:
        """Generate complete response (non-streaming)."""
        ...
    
    @abstractmethod
    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        config: AIRequestConfig = None,
    ) -> AsyncGenerator[AIResponseChunk, None]:
        """Generate response with streaming chunks."""
        ...
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Verify provider connectivity."""
        ...
