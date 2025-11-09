"""ThreadRepository Protocol - Abstract interface for thread persistence."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.message import Message
from ..entities.thread import Thread
from ..value_objects.thread_id import ThreadId


class ThreadRepository(ABC):
    """
    Abstract repository interface for Thread persistence.

    Defines the contract that infrastructure must implement.
    Follows Dependency Inversion Principle - domain defines the abstraction.
    """

    @abstractmethod
    async def create_thread(self, thread: Thread) -> Thread:
        """
        Create a new thread.

        Args:
            thread: Thread entity to persist

        Returns:
            Thread with generated ID

        Raises:
            RepositoryError: If creation fails
        """
        pass

    @abstractmethod
    async def get_thread_by_id(self, thread_id: ThreadId) -> Optional[Thread]:
        """
        Retrieve a thread by its ID.

        Args:
            thread_id: Thread identifier

        Returns:
            Thread if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_thread_with_messages(
        self, thread_id: ThreadId
    ) -> Optional[Thread]:
        """
        Retrieve a thread with all its messages loaded.

        Args:
            thread_id: Thread identifier

        Returns:
            Thread with messages if found, None otherwise
        """
        pass

    @abstractmethod
    async def save_message(self, message: Message) -> Message:
        """
        Save a message to a thread.

        Business rule: Thread must exist.

        Args:
            message: Message entity to persist

        Returns:
            Message with generated ID

        Raises:
            RepositoryError: If thread doesn't exist or save fails
        """
        pass

    @abstractmethod
    async def get_messages_by_thread(
        self, thread_id: ThreadId, limit: Optional[int] = None
    ) -> List[Message]:
        """
        Retrieve all messages for a thread.

        Args:
            thread_id: Thread identifier
            limit: Maximum number of messages to return (None = all)

        Returns:
            List of messages in chronological order
        """
        pass

    @abstractmethod
    async def delete_thread(self, thread_id: ThreadId) -> bool:
        """
        Delete a thread and all its messages.

        Args:
            thread_id: Thread identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def thread_exists(self, thread_id: ThreadId) -> bool:
        """
        Check if a thread exists.

        Args:
            thread_id: Thread identifier

        Returns:
            True if thread exists
        """
        pass

    @abstractmethod
    async def update_thread_metadata(
        self, thread_id: ThreadId, metadata: dict
    ) -> bool:
        """
        Update thread metadata.

        Args:
            thread_id: Thread identifier
            metadata: New metadata dictionary

        Returns:
            True if updated, False if not found
        """
        pass

    @abstractmethod
    async def list_all_threads(self) -> List[Thread]:
        """
        List all threads.

        Returns:
            List of all threads (without messages loaded)
        """
        pass
