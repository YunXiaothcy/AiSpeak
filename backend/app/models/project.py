"""
Project and related models.
"""

import json
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Project(Base):
    """Novel writing project."""
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft/published/archived
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    settings = relationship("NovelSettings", back_populates="project", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, title='{self.title}')>"


class NovelSettings(Base):
    """Novel-specific settings for a project."""
    __tablename__ = "novel_settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), unique=True, nullable=False)
    genre: Mapped[str] = mapped_column(String(100), default="现代")
    theme: Mapped[str] = mapped_column(Text, default="")
    target_chapters: Mapped[str] = mapped_column(String(20), default="20")
    writing_style: Mapped[str] = mapped_column(Text, default="")
    target_audience: Mapped[str] = mapped_column(String(100), default="成人读者")
    plot_summary: Mapped[str] = mapped_column(Text, default="")
    world_rules: Mapped[str] = mapped_column(Text, default="")
    style_guide: Mapped[str] = mapped_column(Text, default="")
    pov: Mapped[str] = mapped_column(String(50), default="第三人称")
    tone: Mapped[str] = mapped_column(String(50), default="严肃")
    timeline_events: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    
    # Relationships
    project = relationship("Project", back_populates="settings")


class Chapter(Base):
    """Novel chapter with content."""
    __tablename__ = "chapters"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(255), default="未命名章节")
    content: Mapped[str] = mapped_column(Text, default="")
    outline: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    word_count_target: Mapped[str] = mapped_column(String(50), default="2000-3000字")
    characters_in_scene: Mapped[str] = mapped_column(Text, default="[]")  # JSON array of IDs
    scene_setting: Mapped[str] = mapped_column(Text, default="")
    emotional_tone: Mapped[str] = mapped_column(String(50), default="")
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft/revised/final
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="chapters")
    ai_sessions = relationship("AISession", back_populates="chapter", cascade="all, delete-orphan")
    
    @property
    def character_ids(self) -> list:
        """Parse character IDs from JSON."""
        try:
            return json.loads(self.characters_in_scene)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def __repr__(self) -> str:
        return f"<Chapter(id={self.id}, title='{self.title}', order={self.order_index})>"


class Character(Base):
    """Character in a novel."""
    __tablename__ = "characters"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="配角")  # 主角/反派/配角/NPC
    age: Mapped[str] = mapped_column(String(50), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    personality: Mapped[str] = mapped_column(Text, default="")
    appearance: Mapped[str] = mapped_column(Text, default="")
    abilities: Mapped[str] = mapped_column(Text, default="")
    relationships: Mapped[str] = mapped_column(Text, default="")
    background: Mapped[str] = mapped_column(Text, default="")
    speech_pattern: Mapped[str] = mapped_column(Text, default="")
    current_status: Mapped[str] = mapped_column(String(100), default="正常")
    notes: Mapped[str] = mapped_column(Text, default="")
    
    # Relationships
    project = relationship("Project", back_populates="characters")
    
    def __repr__(self) -> str:
        return f"<Character(id={self.id}, name='{self.name}', role='{self.role}')>"


class AISession(Base):
    """AI generation session record."""
    __tablename__ = "ai_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(Integer, ForeignKey("chapters.id"), nullable=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)  # outline/chapter/continuation/polish/consistency/dialogue
    model_used: Mapped[str] = mapped_column(String(100), default="")
    prompt_template: Mapped[str] = mapped_column(Text, default="")
    full_response: Mapped[str] = mapped_column(Text, default="")
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chapter = relationship("Chapter", back_populates="ai_sessions")
    
    def __repr__(self) -> str:
        return f"<AISession(id={self.id}, task='{self.task_type}', model='{self.model_used}')>"
