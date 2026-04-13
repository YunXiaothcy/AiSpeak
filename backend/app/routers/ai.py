"""
AI Generation API routes with streaming support.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.core.database import get_db
from app.schemas.project import GenerateRequest, ModelInfo
from app.services.ai_generation.ai_service import AIGenerationService
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Generation"])


@router.post("/generate/stream")
async def generate_streaming(
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI content with Server-Sent Events streaming.
    
    Returns text/event-stream with real-time chunks.
    """
    service = AIGenerationService()
    
    # Mock project data (would fetch from DB in production)
    project_data = {
        "genre": "奇幻",
        "theme": "冒险",
        "target_chapters": "20",
        "writing_style": "细腻描写",
        "characters": [],
        "chapters": [],
        "world_rules": "",
        "timeline_events": "[]",
    }
    
    chapter_data = None
    if request.chapter_id:
        chapter_data = {"id": request.chapter_id}
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Yield SSE-formatted events."""
        try:
            async for chunk in service.generate_content(
                task_type=request.task_type,
                project_data=project_data,
                chapter_data=chapter_data,
                model=request.model,
                **(request.options or {}),
            ):
                data = {
                    "content": chunk.content,
                    "is_final": chunk.is_final,
                    "metadata": chunk.metadata,
                }
                yield f"data: {json.dumps(data)}\n\n"
                
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            error_data = {"error": True, "message": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/models", response_model=list[ModelInfo])
async def list_models():
    """List available AI models."""
    service = AIGenerationService()
    models = await service.list_models()
    return [ModelInfo(**m) for m in models]


@router.get("/templates")
async def list_templates():
    """List available prompt templates."""
    service = AIGenerationService()
    templates = await service.list_templates()
    return templates


@router.post("/consistency-check")
async def consistency_check(request: dict, db: AsyncSession = Depends(get_db)):
    """Run consistency check on content (placeholder)."""
    # Would implement full consistency checking logic
    return {
        "issues": [],
        "total_issues": 0,
        "has_critical": False,
        "summary": "Consistency check completed.",
    }
