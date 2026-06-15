from abc import ABC, abstractmethod
from collections.abc import Iterable

from src.models.chunk import Chunk


class RepositoryInterface(ABC):
    """
    Abstract interface for chunk repository implementations.
    
    Defines the contract for storing and retrieving document chunks.
    Implementations must ensure data integrity, thread-safety if needed,
    and consistent behavior across all operations.
    
    Expected behavior:
    - add_chunks: Appends chunks to existing collection (does not replace)
    - get_chunks: Returns a defensive copy to prevent external mutation
    - clear: Removes all chunks, resetting repository to empty state
    - count: Returns current number of stored chunks
    
    Error handling contract:
    - add_chunks: Must raise TypeError for non-Chunk items, ValueError for None/empty
    - get_chunks: Must never return None; returns empty list if no chunks exist
    - Operations must preserve repository invariants even on partial failures
    """

    @abstractmethod
    def add_chunks(self, chunks: Iterable[Chunk]) -> None:
        """
        Add chunks to the repository.
        
        Chunks are appended to existing collection. Duplicates are allowed
        unless implementation provides deduplication logic.
        
        Args:
            chunks: Iterable of Chunk instances to store
            
        Raises:
            TypeError: If chunks is not iterable or contains non-Chunk instances
            ValueError: If chunks is None or empty
            RepositoryException: If storage operation fails
            
        Implementation notes:
            - Must validate all chunks before modifying state
            - Should be atomic: either all chunks added or none
            - Must preserve order of input chunks
        """
        raise NotImplementedError("Subclasses must implement add_chunks")

    @abstractmethod
    def get_chunks(self) -> list[Chunk]:
        """
        Retrieve all stored chunks.
        
        Returns a defensive copy to prevent external mutation of internal state.
        Chunks are returned in insertion order.
        
        Returns:
            List of all Chunk instances (copy, not reference to internal storage)
            Returns empty list if repository is empty, never None
            
        Raises:
            RepositoryException: If retrieval operation fails
            
        Implementation notes:
            - Must return a copy, not a reference to internal storage
            - Ordering must be stable and predictable (typically insertion order)
        """
        raise NotImplementedError("Subclasses must implement get_chunks")

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all chunks from the repository.
        
        Resets repository to empty state. This operation is typically not reversible.
        
        Raises:
            RepositoryException: If clear operation fails
            
        Implementation notes:
            - Must be idempotent (calling multiple times has same effect)
            - Should release resources if applicable (memory, file handles, etc.)
        """
        raise NotImplementedError("Subclasses must implement clear")

    @abstractmethod
    def count(self) -> int:
        """
        Return the total number of chunks in the repository.
        
        Returns:
            Non-negative integer count of stored chunks
            
        Raises:
            RepositoryException: If count operation fails
            
        Implementation notes:
            - Must return 0 for empty repository
            - Count should reflect current state after any add/clear operations
        """
        raise NotImplementedError("Subclasses must implement count")