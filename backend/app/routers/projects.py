"""
Project and Chapter API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    CharacterCreate,
    CharacterResponse,
)
from app.models.project import Project, Chapter, Character
from app.repositories.project_repo import ProjectRepository
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/projects", tags=["Projects"])


# ========== Project Endpoints ==========

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all projects (would filter by user in production)."""
    repo = ProjectRepository(db)
    # For now, return all (in production, would pass user_id)
    result = await db.execute(Project.__table__.select().offset(skip).limit(limit))
    projects = result.scalars().all()
    return [
        ProjectResponse(
            id=p.id,
            title=p.title,
            user_id=p.user_id,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
            chapter_count=len(p.chapters) if p.chapters else 0,
            character_count=len(p.characters) if p.characters else 0,
        )
        for p in projects
    ]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new novel project."""
    new_project = Project(
        title=project_data.title,
        user_id=1,  # TODO: Get from auth
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return ProjectResponse(
        id=new_project.id,
        title=new_project.title,
        user_id=new_project.user_id,
        status=new_project.status,
        created_at=new_project.created_at,
        updated_at=new_project.updated_at,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get project by ID."""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(
        id=project.id,
        title=project.title,
        user_id=project.user_id,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        chapter_count=len(project.chapters) if project.chapters else 0,
        character_count=len(project.characters) if project.characters else 0,
    )


# ========== Chapter Endpoints ==========

@router.get("/{project_id}/chapters", response_model=List[ChapterResponse])
async def list_chapters(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get all chapters for a project."""
    result = await db.execute(
        Chapter.__table__.select()
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.order_index)
    )
    chapters = result.scalars().all()
    return [ChapterResponse.model_validate(ch) for ch in chapters]


@router.post("/{project_id}/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    project_id: int,
    chapter_data: ChapterCreate,
    db: AsyncSession = Depends(get_db):
    """Create a new chapter in a project."""
    # Get next order index
    result = await db.execute(
        Chapter.__table__.select()
        .where(Chapter.project_id == project_id)
    )
    existing_chapters = result.scalars().all()
    next_order = len(existing_chapters) + 1
    
    new_chapter = Chapter(
        project_id=project_id,
        title=chapter_data.title,
        outline=chapter_data.outline,
        word_count_target=chapter_data.word_count_target,
        order_index=next_order,
    )
    
    db.add(new_chapter)
    await db.commit()
    await db.refresh(new_chapter)
    
    return ChapterResponse.model_validate(new_chapter)


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(chapter_id: int, db: AsyncSession = Depends(get_db)):
    """Get chapter by ID with content."""
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return ChapterResponse.model_validate(chapter)


@router.put("/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: int,
    chapter_data: ChapterUpdate,
    db: AsyncSession = Depends(get_db):
    """Update chapter content."""
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    update_data = chapter_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)
    
    await db.commit()
    await db.refresh(chapter)
    
    return ChapterResponse.model_validate(chapter)


# ========== Character Endpoints ==========

@router.get("/{project_id}/characters", response_model=List[CharacterResponse])
async def list_characters(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get all characters for a project."""
    result = await db.execute(
        Character.__table__.select().where(Character.project_id == project_id)
    )
    characters = result.scalars().all()
    return [CharacterResponse.model_validate(c) for c in characters]


@router.post("/{project_id}/characters", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    project_id: int,
    char_data: CharacterCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new character in a project."""
    new_char = Character(
        project_id=project_id,
        name=char_data.name,
        role=char_data.role,
        age=char_data.age,
        gender=char_data.gender,
        personality=char_data.personality,
        appearance=char_data.appearance,
        speech_pattern=char_data.speech_pattern,
    )
    
    db.add(new_char)
    await db.commit()
    await db.refresh(new_char)
    
    return CharacterResponse.model_validate(new_char)
