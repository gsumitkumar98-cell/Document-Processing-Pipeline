from typing import Optional, Any


class PipelineException(Exception):
    """
    Base exception for all pipeline-related errors.
    
    Provides structured context for debugging including the operation that failed,
    additional details, and optional exception chaining.
    
    Attributes:
        message: Human-readable error description
        operation: The operation or stage that failed (e.g., "document_loading", "chunking")
        details: Additional context as a dictionary (file paths, parameters, etc.)
        original_exception: The underlying exception if this wraps another error
        
    Example:
        raise PipelineException(
            message="Failed to process document",
            operation="document_loading",
            details={"file_path": "/path/to/doc.txt"}
        )
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ) -> None:
        self.message = message
        self.operation = operation
        self.details = details or {}
        self.original_exception = original_exception
        
        full_message = f"{message}"
        if operation:
            full_message = f"[{operation}] {full_message}"
        if details:
            full_message = f"{full_message} | Details: {details}"
        
        super().__init__(full_message)
    
    def __str__(self) -> str:
        return super().__str__()


class DocumentLoadException(PipelineException):
    """
    Raised when document loading or reading fails.
    
    This should be raised when:
    - File cannot be found or accessed
    - File format is unsupported or corrupted
    - File encoding issues prevent reading
    - Permission errors occur during file access
    
    Example:
        raise DocumentLoadException(
            message="Failed to read document",
            operation="file_read",
            details={"file_path": path, "encoding": "utf-8"},
            original_exception=e
        )
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ) -> None:
        enriched_details = details or {}
        if file_path:
            enriched_details["file_path"] = file_path
        
        super().__init__(
            message=message,
            operation="document_loading",
            details=enriched_details,
            original_exception=original_exception
        )


class ChunkingException(PipelineException):
    """
    Raised when text chunking or segmentation fails.
    
    This should be raised when:
    - Invalid chunk parameters (size, overlap) are provided
    - Text cannot be properly segmented
    - Chunking algorithm encounters malformed input
    
    Example:
        raise ChunkingException(
            message="Invalid chunk size",
            details={"chunk_size": size, "max_allowed": 10000},
            original_exception=e
        )
    """

    def __init__(
        self,
        message: str,
        document_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ) -> None:
        enriched_details = details or {}
        if document_id:
            enriched_details["document_id"] = document_id
        
        super().__init__(
            message=message,
            operation="chunking",
            details=enriched_details,
            original_exception=original_exception
        )


class RepositoryException(PipelineException):
    """
    Raised when repository operations fail.
    
    This should be raised when:
    - Data validation fails during add/update operations
    - Repository state becomes inconsistent
    - Storage backend errors occur
    - Query operations fail
    
    Example:
        raise RepositoryException(
            message="Invalid chunk data",
            details={"chunk_count": len(chunks), "validation_error": error},
            original_exception=e
        )
    """

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ) -> None:
        super().__init__(
            message=message,
            operation="repository",
            details=details,
            original_exception=original_exception
        )


class RetrievalException(PipelineException):
    """
    Raised when search or retrieval operations fail.
    
    This should be raised when:
    - Search query is invalid or malformed
    - Retrieval algorithm encounters errors
    - Search backend is unavailable
    - Results cannot be ranked or filtered
    
    Example:
        raise RetrievalException(
            message="Search query too short",
            details={"query": query, "min_length": 2},
            original_exception=e
        )
    """

    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ) -> None:
        enriched_details = details or {}
        if query:
            enriched_details["query"] = query
        
        super().__init__(
            message=message,
            operation="retrieval",
            details=enriched_details,
            original_exception=original_exception
        )