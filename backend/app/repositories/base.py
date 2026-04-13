"""
Generic repository interface and base implementation.
"""

from typing import TypeVar, Generic, List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic repository with CRUD operations.
    
    All repositories should inherit from this class for consistent
    data access patterns.
    """
    
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Get a single entity by primary key."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[T]:
        """Get multiple entities with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        
        # Apply filters dynamically
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def update(self, id: int, data: dict) -> Optional[T]:
        """Update an existing entity."""
        entity = await self.get_by_id(id)
        if not entity:
            return None
        
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def delete(self, id: int) -> bool:
        """Delete an entity by ID."""
        entity = await self.get_by_id(id)
        if not entity:
            return False
        
        await self.session.delete(entity)
        await self.session.flush()
        return True
    
    async def get_or_404(self, id: int, resource_name: str = "Resource") -> T:
        """Get entity or raise 404 error."""
        entity = await self.get_by_id(id)
        if not entity:
            raise NotFoundError(resource_name, id)
        return entity
