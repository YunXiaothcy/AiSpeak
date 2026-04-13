"""
Context builder for assembling AI prompt context from database.
"""

from typing import Dict, Any, Optional
import json

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ContextBuilder:
    """
    Builds context dictionaries for prompt templates.
    
    Extracts relevant information from project data to populate
    template variables like {{GENRE}}, {{CHARACTERS_PRESENT}}, etc.
    """
    
    @staticmethod
    def build_context(
        task_type: str,
        project_data: dict,
        chapter_data: Optional[dict] = None,
        editor_content: str = "",
        **extra_vars: Any,
    ) -> Dict[str, Any]:
        """
        Build complete context for a specific task type.
        
        Args:
            task_type: Type of AI task (outline/chapter/continuation/etc.)
            project_data: Dictionary containing project settings and data
            chapter_data: Optional current chapter being edited
            editor_content: Current text in the editor
            **extra_vars: Additional custom variables
            
        Returns:
            Dictionary of all template variables
        """
        base_context = {
            # Project-level variables
            "GENRE": project_data.get("genre", "奇幻"),
            "THEME": project_data.get("theme", "成长与冒险"),
            "CHARACTER_COUNT": str(len(project_data.get("characters", []))),
            "TARGET_CHAPTERS": project_data.get("target_chapters", "20"),
            "WRITING_STYLE": project_data.get("writing_style", ""),
            
            # Editor-related
            "EXISTING_CONTENT": editor_content[-2000:] if len(editor_content) > 2000 else editor_content,
            "LAST_PARAGRAPH": ContextBuilder._get_last_paragraph(editor_content),
            
            # Check-related
            "CONTENT_TO_CHECK": editor_content,
            "CHARACTER_DATABASE": ContextBuilder._build_character_db(project_data.get("characters", [])),
            "TIMELINE": project_data.get("timeline_events", "暂无时间线记录"),
            "WORLD_RULES": project_data.get("world_rules", ""),
            
            # Polish-related
            "ORIGINAL_TEXT": extra_vars.get("selected_text", editor_content),
            "POLISH_TYPE": extra_vars.get("polish_type", "全面润色"),
            "STYLE_GUIDE": project_data.get("style_guide", ""),
        }
        
        # Add chapter-specific context if available
        if chapter_data:
            chapters = project_data.get("chapters", [])
            current_idx = next(
                (i for i, ch in enumerate(chapters) if ch.get("id") == chapter_data.get("id")),
                None
            )
            
            base_context.update({
                "PREVIOUS_CONTEXT": ContextBuilder._build_previous_context(chapters, current_idx),
                "CHAPTER_OUTLINE": chapter_data.get("outline", "待填写本章大纲"),
                "CHARACTERS_PRESENT": ContextBuilder._format_characters(
                    project_data.get("characters", []),
                    chapter_data.get("character_ids", [])
                ),
                "WORD_COUNT_TARGET": chapter_data.get("word_count_target", "2000-3000字"),
            })
        else:
            base_context.update({
                "PREVIOUS_CONTEXT": "这是故事的开篇。",
                "CHAPTER_OUTLINE": "",
                "CHARACTERS_PRESENT": "[尚未设定角色]",
                "WORD_COUNT_TARGET": "2000-3000字",
            })
        
        # Merge extra variables
        base_context.update(extra_vars)
        
        # Ensure no empty values (use placeholder)
        return {
            k: (v if v else "[待填写]")
            for k, v in base_context.items()
        }
    
    @staticmethod
    def _get_last_paragraph(text: str) -> str:
        """Get the last paragraph from text."""
        paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
        return paragraphs[-1] if paragraphs else ""
    
    @staticmethod
    def _build_previous_context(chapters: list, current_idx: Optional[int]) -> str:
        """Build summary of previous chapters."""
        if current_idx is None or current_idx == 0:
            return "这是故事的第一章。"
        
        summaries = []
        for ch in chapters[:current_idx]:
            summary = ch.get("summary", "") or ch.get("content", "")[:200]
            title = ch.get("title", "")
            summaries.append(f"第{chapters.index(ch)+1}章《{title}》: {summary}...")
        
        return "\n".join(summaries) if summaries else "前文情节发展中。"
    
    @staticmethod
    def _format_characters(characters: list, character_ids: list = None) -> str:
        """Format character information for prompts."""
        if not characters:
            return "[尚未设定角色]"
        
        formatted = []
        for char in characters[:6]:  # Limit to avoid token overflow
            if character_ids and char.get("id") not in character_ids and character_ids:
                continue
                
            formatted.append(
                f"- {char.get('name', '?')}: "
                f"{char.get('role', '配角')} | "
                f"{char.get('personality', '性格待补充')} | "
                f"{char.get('appearance', '外貌待补充')}"
            )
        
        return "\n".join(formatted) if formatted else "[未指定出场角色]"
    
    @staticmethod
    def _build_character_db(characters: list) -> str:
        """Build detailed character database string."""
        if not characters:
            return "[无角色数据]"
        
        entries = []
        for char in characters:
            entry = f"""【{char.get('name', '未知')}】
- 身份: {char.get('role', '?')}
- 性格: {char.get('personality', '?')}
- 外貌: {char.get('appearance', '?')}
- 能力: {char.get('abilities', '无')}
- 关系: {char.get('relationships', '?')}
- 背景: {char.get('background', '?')}
- 语言特点: {char.get('speech_pattern', '?')}"""
            entries.append(entry)
        
        return "\n\n".join(entries)
