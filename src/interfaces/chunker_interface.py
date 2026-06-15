from abc import ABC, abstractmethod

from src.models.document import Document
from src.models.chunk import Chunk


class ChunkerInterface(ABC):
    """
    Abstract interface for document chunking implementations.
    
    Defines the contract for splitting documents into smaller text segments
    suitable for processing, retrieval, and LLM consumption.
    
    Design principles:
    - Metadata preservation: Chunks retain document ID and name for traceability
    - Sequential IDs: Chunks numbered sequentially starting from 1
    - Content integrity: Original text meaning preserved across chunks
    - Deterministic: Same document produces same chunks given same configuration
    
    Common chunking strategies:
    - Fixed-size word chunking (simple, fast)
    - Sentence-aware splitting (preserves semantic boundaries)
    - Paragraph-based chunking (document structure aware)
    - Sliding window with overlap (context preservation)
    - Semantic chunking (embedding-based similarity)
    """

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """
        Split a document into smaller text chunks.
        
        Processes document content and creates a sequence of Chunk objects
        with appropriate metadata and sequential IDs.
        
        Args:
            document: Document object to chunk
                - Must have valid content attribute (str)
                - Must have document_id attribute (str)
                - Must have file_name attribute (str)
                - Content can be empty (returns empty list)
        
        Returns:
            List of Chunk objects, each containing:
                - document_id: Same as input document's ID
                - document_name: Same as input document's file_name
                - chunk_id: Sequential integer starting from 1
                - text: Chunk content (non-empty string)
            
            Chunks are ordered sequentially (chunk_id 1, 2, 3, ...).
            Empty list returned for empty/whitespace-only documents.
            Never returns None.
        
        Raises:
            ValueError: If document is None or missing required attributes
            TypeError: If document attributes have wrong types
            ChunkingException: If chunking operation fails (encoding issues,
                              invalid configuration, or implementation errors)
        
        Input validation requirements:
            - Document: Must validate presence of content, document_id, file_name
            - Content type: Must be string (not bytes or other types)
            - Content validity: Should handle None, empty, whitespace-only gracefully
            - Attributes: Should fail fast if document lacks required attributes
        
        Chunking behavior contract:
            - Chunk IDs start at 1 (not 0)
            - No gaps in chunk ID sequence
            - All chunks from same document share same document_id
            - Chunk text should be non-empty (empty chunks typically filtered)
            - Original content reconstructible from chunks (with possible 
              whitespace normalization)
            - Chunks maintain original content order
        
        Edge cases to handle:
            - Empty document content: Return empty list
            - Whitespace-only content: Return empty list (or single chunk if desired)
            - Content shorter than chunk size: Return single chunk
            - Very large documents: Should not fail, may warn on memory
            - Unicode/emoji content: Must handle properly without corruption
            - Malformed document object: Raise clear validation error
        
        Metadata handling:
            - document_id: Use input document's ID unchanged
            - document_name: Use input document's file_name unchanged
            - chunk_id: Generate sequentially, starting from 1
            - Additional metadata (positions, offsets): Implementation-specific
        
        Performance considerations:
            - Should handle documents up to several MB efficiently
            - Memory usage should scale linearly with document size
            - For very large documents, consider streaming/generator approach
        
        Configuration notes:
            - Chunk size, overlap, and strategy are implementation-specific
            - Configuration typically passed to __init__, not chunk()
            - Same configuration should produce deterministic results
        
        Example:
            >>> chunker = TextChunker(chunk_size=100, overlap=20)
            >>> chunks = chunker.chunk(document)
            >>> for chunk in chunks:
            ...     print(f"Chunk {chunk.chunk_id}: {chunk.text[:50]}...")
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement chunk() method"
        )