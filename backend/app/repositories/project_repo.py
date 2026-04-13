"""
Project repository for database operations.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.project import Project


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project entities."""
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Project)
    
    async def get_by_user_id(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[Project]:
        """Get all projects for a specific user."""
        result = await self.session.execute(
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_chapters(self, project_id: int) -> int:
        """Count chapters in a project."""
        from app.models.project import Chapter
        result = await self.session.execute(
            select(func.count(Chapter.id))
            .where(Chapter.project_id == project_id)
        )
        return result.scalar() or 0
    
    async def count_characters(self, project_id: int) -> int:
        """Count characters in a project."""
        from app.models.project import Character
        result = await self.session.execute(
            select(func.count(Character.id))
            .where(Character.project_id == project_id)
        )
        return result.scalar() or 0
