"""
AI Prompt Template Manager.

Loads and renders prompts from backend/prompts/ directory.
All system prompts are loaded from external template files - NEVER hardcoded.
"""

import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.config import settings
from app.core.exceptions import PromptTemplateError
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class PromptTemplateManager:
    """
    Manages AI prompt templates with Jinja2 rendering.
    
    Templates are stored in backend/prompts/ as .txt files.
    Each template contains:
    - [CUSTOM_SYSTEM_PROMPT_HERE] placeholder for system instructions
    - {{VARIABLE}} placeholders for dynamic content
    """
    
    TEMPLATE_MAPPING = {
        "outline": "outline_prompt.txt",
        "chapter": "chapter_prompt.txt",
        "continuation": "continuation_prompt.txt",
        "polish": "polish_prompt.txt",
        "consistency": "consistency_prompt.txt",
        "dialogue": "dialogue_prompt.txt",
    }
    
    SYSTEM_PROMPT_MARKER = "[CUSTOM_SYSTEM_PROMPT_HERE]"
    USER_INPUT_MARKER = "[用户输入]"
    
    def __init__(self, prompts_dir: Optional[str] = None) -> None:
        self.prompts_dir = Path(prompts_dir or settings.PROMPTS_DIR)
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._template_cache: Dict[str, str] = {}
        
        logger.info(f"PromptTemplateManager initialized: {self.prompts_dir}")
    
    def load_template(self, template_name: str) -> str:
        """Load raw template content from file."""
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        filename = self.TEMPLATE_MAPPING.get(template_name)
        if not filename:
            raise PromptTemplateError(
                template_name,
                reason=f"unknown. Available: {list(self.TEMPLATE_MAPPING.keys())}"
            )
        
        filepath = self.prompts_dir / filename
        
        if not filepath.exists():
            raise PromptTemplateError(template_name, reason=f"file not found: {filepath}")
        
        try:
            content = filepath.read_text(encoding="utf-8")
            self._template_cache[template_name] = content
            logger.debug(f"Loaded template '{template_name}' ({len(content)} chars)")
            return content
        except IOError as e:
            raise PromptTemplateError(template_name, reason=str(e))
    
    def render_template(
        self,
        template_name: str,
        **variables: Any
    ) -> Tuple[str, str]:
        """
        Render template with variables.
        
        Returns:
            Tuple[str, str]: (system_prompt, user_prompt)
        """
        raw_template = self.load_template(template_name)
        
        try:
            rendered = self._jinja_env.from_string(raw_template).render(**variables)
        except Exception as e:
            raise PromptTemplateError(template_name, reason=f"rendering error: {e}")
        
        # Split into system and user prompts
        if self.SYSTEM_PROMPT_MARKER in rendered:
            parts = rendered.split(self.SYSTEM_PROMPT_MARKER, 1)
            system_prompt = parts[0].strip() if parts[0].strip() else ""
            remaining = parts[1].strip() if len(parts) > 1 else rendered
        else:
            system_prompt = ""
            remaining = rendered
        
        # Extract user portion
        if self.USER_INPUT_MARKER in remaining:
            user_parts = remaining.split(self.USER_INPUT_MARKER, 1)
            context = user_parts[0].strip()
            user_query = user_parts[1].strip() if len(user_parts) > 1 else ""
            user_prompt = f"{context}\n\n{user_query}" if context else user_query
        else:
            user_prompt = remaining
        
        logger.info(
            f"Rendered '{template_name}': "
            f"system={len(system_prompt)}chars, user={len(user_prompt)}chars"
        )
        
        return system_prompt, user_prompt
    
    def list_available_templates(self) -> Dict[str, str]:
        """List all available templates."""
        return {
            name: str(self.prompts_dir / filename)
            for name, filename in self.TEMPLATE_MAPPING.items()
            if (self.prompts_dir / filename).exists()
        }
    
    def reload_templates(self) -> None:
        """Clear template cache to force reload."""
        self._template_cache.clear()
        logger.info("Template cache cleared")
