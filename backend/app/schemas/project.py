"""
Project, Chapter, Character, and AI-related schemas.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


# ========== Project Schemas ==========

class NovelSettingsBase(BaseModel):
    """Base schema for novel settings."""
    genre: str = "现代"
    theme: str = ""
    target_chapters: str = "20"
    writing_style: str = ""
    target_audience: str = "成人读者"
    plot_summary: str = ""
    world_rules: str = ""
    style_guide: str = ""
    pov: str = "第三人称"
    tone: str = "严肃"


class NovelSettingsCreate(NovelSettingsBase):
    """Schema for creating novel settings."""
    pass


class NovelSettingsResponse(NovelSettingsBase):
    """Schema for novel settings response."""
    id: int
    project_id: int
    timeline_events: str = "[]"
    
    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Base project schema."""
    title: str = Field(..., min_length=1, max_length=255)


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    settings: Optional[NovelSettingsCreate] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    chapter_count: int = 0
    character_count: int = 0
    
    class Config:
        from_attributes = True


# ========== Chapter Schemas ==========

class ChapterBase(BaseModel):
    """Base chapter schema."""
    title: str = "未命名章节"
    outline: str = ""


class ChapterCreate(ChapterBase):
    """Schema for creating a chapter."""
    word_count_target: str = "2000-3000字"


class ChapterUpdate(BaseModel):
    """Schema for updating a chapter."""
    title: Optional[str] = None
    content: Optional[str] = None
    outline: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    order_index: Optional[int] = None


class ChapterResponse(ChapterBase):
    """Schema for chapter response."""
    id: int
    project_id: int
    order_index: int
    content: str = ""
    summary: str = ""
    word_count_target: str = "2000-3000字"
    status: str = "draft"
    created_at: datetime
    updated_at: Optional[datetime]
    
    @property
    def word_count(self) -> int:
        return len(self.content.replace(" ", ""))
    
    class Config:
        from_attributes = True


# ========== Character Schemas ==========

class CharacterBase(BaseModel):
    """Base character schema."""
    name: str = Field(..., min_length=1, max_length=100)
    role: str = "配角"


class CharacterCreate(CharacterBase):
    """Schema for creating a character."""
    age: Optional[str] = None
    gender: Optional[str] = None
    personality: str = ""
    appearance: str = ""
    abilities: str = ""
    relationships: str = ""
    background: str = ""
    speech_pattern: str = ""


class CharacterUpdate(BaseModel):
    """Schema for updating a character."""
    name: Optional[str] = None
    role: Optional[str] = None
    personality: Optional[str] = None
    appearance: Optional[str] = None
    current_status: Optional[str] = None


class CharacterResponse(CharacterBase):
    """Schema for character response."""
    id: int
    project_id: int
    age: Optional[str]
    gender: Optional[str]
    personality: str
    appearance: str
    current_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== AI Generation Schemas ==========

class GenerateRequest(BaseModel):
    """Schema for AI generation request."""
    task_type: str = Field(..., description="outline/chapter/continuation/polish/consistency/dialogue")
    project_id: int
    chapter_id: Optional[int] = None
    model: Optional[str] = None
    options: Optional[dict] = None


class GenerateResponse(BaseModel):
    """Schema for AI generation response."""
    task_id: str
    task_type: str
    status: str = "completed"
    content: str = ""
    model_used: str = ""
    token_count: int = 0
    duration_seconds: float = 0.0


class ModelInfo(BaseModel):
    """Schema for AI model information."""
    id: str
    name: str
    provider: str


class ConsistencyCheckRequest(BaseModel):
    """Schema for consistency check request."""
    content: str
    project_id: int
    check_types: List[str] = ["character", "plot", "timeline", "world"]


class ConsistencyIssue(BaseModel):
    """Schema for a single consistency issue."""
    severity: str  # critical/warning/info
    category: str  # character/plot/timeline/world
    location: str  # where in text
    description: str
    suggestion: str


class ConsistencyCheckResponse(BaseModel):
    """Schema for consistency check response."""
    issues: List[ConsistencyIssue]
    total_issues: int
    has_critical: bool
    summary: str


# ========== Export Schemas ==========

class ExportRequest(BaseModel):
    """Schema for export request."""
    project_id: int
    format: str = "md"  # md/txt/docx
    include_metadata: bool = True
    chapter_ids: Optional[List[int]] = None


class ExportResponse(BaseModel):
    """Schema for export response."""
    job_id: str
    status: str = "processing"
    download_url: Optional[str] = None
