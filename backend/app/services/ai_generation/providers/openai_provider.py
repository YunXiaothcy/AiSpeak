"""
OpenAI-compatible provider implementation.

Supports GPT-4, Grok, Claude (via proxy), and any OpenAI-compatible API.
"""

import asyncio
from typing import AsyncGenerator, Optional

from openai import AsyncOpenAI

from app.services.ai_generation.providers.base_provider import (
    BaseAIProvider,
    AIProviderType,
    AIRequestConfig,
    AIResponseChunk,
)
from app.core.exceptions import AIProviderError
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class OpenAICompatibleProvider(BaseAIProvider):
    """Provider for OpenAI and compatible APIs with streaming support."""
    
    provider_type = AIProviderType.OPENAI
    supported_models = [
        "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo",
        "grok-beta", "grok-alpha",
        "claude-3-5-sonnet", "claude-3-opus",
    ]
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
    ) -> None:
        super().__init__(api_key, base_url)
        self._client: Optional[AsyncOpenAI] = None
    
    async def initialize(self) -> None:
        """Create async OpenAI client."""
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=60.0,
            max_retries=3,
        )
        logger.info(f"OpenAI provider initialized (base_url={self.base_url})")
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        config: AIRequestConfig = None,
    ) -> str:
        """Generate non-streaming response."""
        if not self._client:
            await self.initialize()
        
        config = config or AIRequestConfig()
        
        try:
            response = await self._client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                stream=False,
            )
            
            return response.choices[0].message.content or ""
               
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise AIProviderError(provider="openai", message=str(e), original_error=e)
    
    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        config: AIRequestConfig = None,
    ) -> AsyncGenerator[AIResponseChunk, None]:
        """Generate streaming response with SSE support."""
        if not self._client:
            await self.initialize()
        
        config = config or AIRequestConfig()
        
        try:
            stream = await self._client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                stream=True,
            )
            
            async for chunk in stream:
                delta = chunk.choices[0].delta
                
                if delta.content:
                    yield AIResponseChunk(
                        content=delta.content,
                        is_final=False,
                        metadata={
                            "model": config.model,
                            "provider": "openai",
                            "finish_reason": chunk.choices[0].finish_reason,
                        }
                    )
            
            # Signal completion
            yield AIResponseChunk(content="", is_final=True)
            
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            yield AIResponseChunk(
                content=f"\n\n❌ Error: {str(e)}",
                is_final=True,
                metadata={"error": True},
            )
    
    async def health_check(self) -> bool:
        """Test API connectivity."""
        if not self._client:
            await self.initialize()
        
        try:
            await self._client.models.list()
            return True
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False
