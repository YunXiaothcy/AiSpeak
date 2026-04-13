"""
Main AI Generation Service - orchestrates all AI operations.
"""

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_generation.prompt_manager import PromptTemplateManager
from app.services.ai_generation.context_builder import ContextBuilder
from app.services.ai_generation.providers.openai_provider import OpenAICompatibleProvider
from app.services.ai_generation.providers.base_provider import (
    AIRequestConfig,
    AIResponseChunk,
)
from app.config import settings
from app.core.exceptions import AIProviderError, PromptTemplateError
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AIGenerationService:
    """
    Main service for AI-powered content generation.
    
    Coordinates prompt management, context building, and provider selection.
    Design Pattern: Facade + Strategy
    """
    
    def __init__(
        self,
        prompt_manager: PromptTemplateManager = None,
        context_builder: ContextBuilder = None,
    ) -> None:
        self.prompt_mgr = prompt_manager or PromptTemplateManager()
        self.ctx_builder = context_builder or ContextBuilder()
        self._providers = {}
        self._default_config = AIRequestConfig(
            model=settings.DEFAULT_AI_MODEL,
            temperature=settings.AI_TEMPERATURE,
            max_tokens=settings.AI_MAX_TOKENS,
            stream=True,
        )
    
    def _get_provider(self, model: str):
        """Get or create provider for model."""
        if model in self._providers:
            return self._providers[model]
        
        # Determine provider based on model name
        if "grok" in model.lower():
            api_key = settings.GROK_API_KEY or settings.OPENAI_API_KEY
            base_url = "https://api.x.ai/v1"
        elif "claude" in model.lower():
            api_key = settings.CLAUDE_API_KEY
            base_url = None
        else:
            api_key = settings.OPENAI_API_KEY
            base_url = settings.OPENAI_BASE_URL
        
        if not api_key:
            raise AIProviderError(
                provider=model.split("-")[0],
                message=f"No API key configured for model: {model}",
            )
        
        provider = OpenAICompatibleProvider(api_key=api_key, base_url=base_url)
        self._providers[model] = provider
        
        logger.info(f"Created provider for model: {model}")
        return provider
    
    async def generate_content(
        self,
        task_type: str,
        project_data: dict,
        chapter_data: Optional[dict] = None,
        editor_content: str = "",
        model: Optional[str] = None,
        **custom_vars,
    ) -> AsyncGenerator[AIResponseChunk, None]:
        """
        Execute AI generation task with streaming.
        
        Args:
            task_type: outline/chapter/continuation/polish/consistency/dialogue
            project_data: Project data dictionary
            chapter_data: Optional current chapter data
            editor_content: Current editor text
            model: Override default model
            **custom_vars: Additional template variables
            
        Yields:
            AIResponseChunk: Streaming text chunks
        """
        logger.info(
            f"Starting AI generation: task={task_type}, "
            f"model={model or settings.DEFAULT_AI_MODEL}"
        )
        
        try:
            # Build context from project data
            context = self.ctx_builder.build_context(
                task_type=task_type,
                project_data=project_data,
                chapter_data=chapter_data,
                editor_content=editor_content,
                **custom_vars,
            )
            
            # Render prompt template
            system_prompt, user_prompt = self.prompt_mgr.render_template(
                template_name=task_type,
                **context,
            )
            
            # Get provider and generate
            provider = self._get_provider(model or self._default_config.model)
            config = AIRequestConfig(
                model=model or self._default_config.model,
                temperature=self._default_config.temperature,
                max_tokens=self._default_config.max_tokens,
                stream=True,
            )
            
            async for chunk in provider.generate_stream(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                config=config,
            ):
                yield chunk
                
        except PromptTemplateError as e:
            logger.error(f"Template error: {e}")
            yield AIResponseChunk(content=f"⚠️ Template Error: {e.message}", is_final=True)
            
        except AIProviderError as e:
            logger.error(f"Provider error: {e}")
            yield AIResponseChunk(content=f"❌ AI Error [{e.provider}]: {e.message}", is_final=True)
            
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            yield AIResponseChunk(content=f"💥 Unexpected error: {str(e)}", is_final=True)
    
    async def list_models(self) -> list[dict]:
        """List available AI models."""
        return [
            {"id": "gpt-4o", "name": "GPT-4o", "provider": "OpenAI"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "OpenAI"},
            {"id": "grok-beta", "name": "Grok Beta", "provider": "xAI"},
            {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet", "provider": "Anthropic"},
        ]
    
    async def list_templates(self) -> dict:
        """List available prompt templates."""
        return self.prompt_mgr.list_available_templates()
