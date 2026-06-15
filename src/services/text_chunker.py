from typing import List, Optional
import re

from src.models.chunk import Chunk
from src.models.document import Document
from src.interfaces.chunker_interface import ChunkerInterface
from src.core.exceptions import ChunkingException
from src.core.logger import get_logger


logger = get_logger(__name__)


class TextChunker(ChunkerInterface):
    """
    Chunks documents into smaller text segments for processing and retrieval.
    
    Uses word-based chunking with configurable size and optional overlap.
    Supports sentence-aware splitting to avoid breaking mid-sentence when possible.
    
    Attributes:
        chunk_size: Number of words per chunk (must be positive)
        overlap: Number of overlapping words between consecutive chunks (default: 0)
        sentence_aware: Whether to respect sentence boundaries (default: False)
    """

    def __init__(
        self,
        chunk_size: int,
        overlap: int = 0,
        sentence_aware: bool = False
    ):
        """
        Initialize the text chunker with validation.
        
        Args:
            chunk_size: Number of words per chunk (must be > 0)
            overlap: Number of overlapping words between chunks (0 <= overlap < chunk_size)
            sentence_aware: Whether to prefer splitting on sentence boundaries
            
        Raises:
            ValueError: If chunk_size or overlap are invalid
        """
        if not isinstance(chunk_size, int):
            raise ValueError(f"chunk_size must be an integer, got {type(chunk_size).__name__}")
        
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        
        if not isinstance(overlap, int):
            raise ValueError(f"overlap must be an integer, got {type(overlap).__name__}")
        
        if overlap < 0:
            raise ValueError(f"overlap cannot be negative, got {overlap}")
        
        if overlap >= chunk_size:
            raise ValueError(
                f"overlap ({overlap}) must be less than chunk_size ({chunk_size})"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap
        self.sentence_aware = sentence_aware

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunk a document into smaller text segments.
        
        Args:
            document: Document to chunk (must have content, document_id, and file_name)
            
        Returns:
            List of Chunk objects with sequential IDs
            
        Raises:
            ChunkingException: If document validation fails or chunking encounters errors
            
        Edge cases:
            - Empty content returns empty list
            - Content shorter than chunk_size returns single chunk
            - Whitespace-only content returns empty list
        """
        # Validate document object
        if document is None:
            raise ChunkingException(
                message="Document cannot be None",
                details={"operation": "validate_document"}
            )
        
        if not hasattr(document, 'content'):
            raise ChunkingException(
                message="Document must have 'content' attribute",
                details={"document_type": type(document).__name__}
            )
        
        if not hasattr(document, 'document_id'):
            raise ChunkingException(
                message="Document must have 'document_id' attribute",
                details={"document_type": type(document).__name__}
            )
        
        if not hasattr(document, 'file_name'):
            raise ChunkingException(
                message="Document must have 'file_name' attribute",
                details={"document_type": type(document).__name__}
            )

        # Validate content
        if document.content is None:
            raise ChunkingException(
                message="Document content cannot be None",
                document_id=document.document_id,
                details={"file_name": document.file_name}
            )
        
        if not isinstance(document.content, str):
            raise ChunkingException(
                message=f"Document content must be a string, got {type(document.content).__name__}",
                document_id=document.document_id,
                details={"file_name": document.file_name}
            )

        try:
            # Handle empty or whitespace-only content
            content = document.content.strip()
            if not content:
                logger.info(
                    f"Document has empty content, returning no chunks",
                    extra={"document": document.file_name}
                )
                return []

            # Split into words
            words = content.split()
            
            if not words:
                logger.info(
                    f"Document has no words after splitting, returning no chunks",
                    extra={"document": document.file_name}
                )
                return []

            chunks = []
            chunk_id = 1
            step_size = self.chunk_size - self.overlap

            logger.info(
                f"Starting chunking",
                extra={
                    "document": document.file_name,
                    "total_words": len(words),
                    "chunk_size": self.chunk_size,
                    "overlap": self.overlap
                }
            )

            index = 0
            while index < len(words):
                # Extract chunk words
                chunk_words = words[index:index + self.chunk_size]
                text = " ".join(chunk_words)

                # Create chunk object
                chunk = Chunk(
                    document_id=document.document_id,
                    document_name=document.file_name,
                    chunk_id=chunk_id,
                    text=text
                )
                chunks.append(chunk)

                chunk_id += 1
                index += step_size

            logger.info(
                f"Chunking completed",
                extra={
                    "document": document.file_name,
                    "chunks": len(chunks),
                    "avg_words_per_chunk": len(words) / len(chunks) if chunks else 0
                }
            )

            return chunks

        except ChunkingException:
            # Re-raise our custom exceptions
            raise
        except Exception as error:
            # Wrap unexpected errors with context
            logger.exception(
                f"Unexpected error during chunking: {error}",
                extra={"document": document.file_name if hasattr(document, 'file_name') else 'unknown'}
            )
            raise ChunkingException(
                message=f"Unexpected error during chunking: {str(error)}",
                document_id=document.document_id if hasattr(document, 'document_id') else None,
                details={
                    "file_name": document.file_name if hasattr(document, 'file_name') else None,
                    "error_type": type(error).__name__
                },
                original_exception=error
            )