"""NoteRepository implementation using SQLAlchemy."""

from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.memory import Note, NoteRepository
from ..sqlalchemy import mappers
from ..sqlalchemy.models import NoteModel


class NoteRepositoryImpl(NoteRepository):
    """
    SQLAlchemy implementation of NoteRepository.

    Implements the repository contract defined in the domain layer.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_note(self, note: Note) -> Note:
        """Create a new note."""
        note_model = mappers.note_entity_to_model(note)
        self.session.add(note_model)
        await self.session.flush()

        return mappers.note_model_to_entity(note_model)

    async def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Retrieve a note by its ID."""
        result = await self.session.execute(
            select(NoteModel).where(NoteModel.id == note_id)
        )
        note_model = result.scalar_one_or_none()

        if not note_model:
            return None

        return mappers.note_model_to_entity(note_model)

    async def get_notes_by_thread(
        self, thread_id: str, limit: Optional[int] = None
    ) -> List[Note]:
        """Get all notes for a thread."""
        query = (
            select(NoteModel)
            .where(NoteModel.thread_id == thread_id)
            .order_by(NoteModel.created_at.desc())
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        note_models = result.scalars().all()

        return [mappers.note_model_to_entity(model) for model in note_models]

    async def get_notes_by_tag(
        self, tag: str, thread_id: Optional[str] = None
    ) -> List[Note]:
        """Get notes by tag, optionally filtered by thread."""
        # Note: SQLite JSON querying is limited, so we'll fetch all and filter in Python
        query = select(NoteModel)

        if thread_id is not None:
            query = query.where(NoteModel.thread_id == thread_id)

        query = query.order_by(NoteModel.created_at.desc())

        result = await self.session.execute(query)
        note_models = result.scalars().all()

        # Filter by tag (case-insensitive)
        tag_lower = tag.lower()
        filtered_notes = [
            mappers.note_model_to_entity(model)
            for model in note_models
            if tag_lower in [t.lower() for t in (model.tags or [])]
        ]

        return filtered_notes

    async def search_notes(
        self, query: str, thread_id: Optional[str] = None
    ) -> List[Note]:
        """Search notes by content or title."""
        search_pattern = f"%{query}%"

        stmt = select(NoteModel).where(
            or_(
                NoteModel.title.ilike(search_pattern),
                NoteModel.content.ilike(search_pattern),
            )
        )

        if thread_id is not None:
            stmt = stmt.where(NoteModel.thread_id == thread_id)

        stmt = stmt.order_by(NoteModel.created_at.desc())

        result = await self.session.execute(stmt)
        note_models = result.scalars().all()

        return [mappers.note_model_to_entity(model) for model in note_models]

    async def update_note(self, note: Note) -> Note:
        """Update an existing note."""
        result = await self.session.execute(
            select(NoteModel).where(NoteModel.id == note.id)
        )
        note_model = result.scalar_one_or_none()

        if not note_model:
            raise ValueError(f"Note {note.id} not found")

        # Update fields
        note_model.title = note.title
        note_model.content = note.content
        note_model.tags = note.tags
        note_model.updated_at = note.updated_at

        await self.session.flush()

        return mappers.note_model_to_entity(note_model)

    async def delete_note(self, note_id: int) -> bool:
        """Delete a note."""
        result = await self.session.execute(
            select(NoteModel).where(NoteModel.id == note_id)
        )
        note_model = result.scalar_one_or_none()

        if not note_model:
            return False

        await self.session.delete(note_model)
        await self.session.flush()
        return True

    async def note_exists(self, note_id: int) -> bool:
        """Check if a note exists."""
        result = await self.session.execute(
            select(NoteModel.id).where(NoteModel.id == note_id)
        )
        return result.scalar_one_or_none() is not None

    async def get_all_tags(self, thread_id: Optional[str] = None) -> List[str]:
        """Get all unique tags, optionally filtered by thread."""
        query = select(NoteModel.tags)

        if thread_id is not None:
            query = query.where(NoteModel.thread_id == thread_id)

        result = await self.session.execute(query)
        all_tags_lists = result.scalars().all()

        # Flatten and deduplicate
        unique_tags = set()
        for tags_list in all_tags_lists:
            if tags_list:
                for tag in tags_list:
                    unique_tags.add(tag)

        return sorted(list(unique_tags))
