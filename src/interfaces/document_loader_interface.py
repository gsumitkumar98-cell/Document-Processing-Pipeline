from abc import ABC, abstractmethod

from src.models.document import Document


class DocumentLoaderInterface(ABC):
    """
    Abstract interface for document loading implementations.
    
    Defines the contract for loading documents from various sources into
    standardized Document objects. Implementations handle file I/O, encoding,
    and format-specific parsing.
    
    Design principles:
    - Source abstraction: Support multiple sources (filesystem, cloud, DB)
    - Encoding awareness: Handle text encoding properly (UTF-8 default)
    - Error transparency: Raise clear exceptions for missing/corrupt files
    - Metadata extraction: Populate document ID and filename
    
    Common implementations:
    - Filesystem loader (local files)
    - Cloud storage loader (S3, GCS, Azure)
    - Database loader (retrieve from DB)
    - HTTP loader (fetch from URLs)
    - Multi-format loader (PDF, DOCX, HTML conversion)
    """

    @abstractmethod
    def load(self, file_path: str) -> Document:
        """
        Load a document from the specified path.
        
        Reads document content from source and creates a Document object
        with appropriate metadata. Handles encoding, validation, and error cases.
        
        Args:
            file_path: Path to document source
                - Filesystem: relative or absolute path (e.g., "docs/file.txt", "/tmp/doc.txt")
                - Cloud: URI format (e.g., "s3://bucket/key", "gs://bucket/object")
                - Database: identifier or query string
                - HTTP: URL (e.g., "https://example.com/doc.txt")
                - Must be non-empty string
                - Path interpretation is implementation-specific
        
        Returns:
            Document object containing:
                - document_id: Unique identifier (path, hash, or URI)
                - file_name: Display name (typically base filename)
                - content: Document text content (string)
            
            Never returns None.
            Empty files return Document with empty content string.
        
        Raises:
            ValueError: If file_path is None, empty, or invalid format
            TypeError: If file_path is not a string
            DocumentLoadException: If loading fails for any reason:
                - File not found or inaccessible
                - Permission denied
                - Unsupported file format
                - Encoding/decoding errors
                - Network errors (for remote sources)
                - Corrupted or malformed file
        
        Input validation requirements:
            - file_path: Must validate type (string), non-empty, format validity
            - Should strip whitespace from path
            - Should normalize paths when appropriate (resolve symlinks, etc.)
            - Invalid paths should raise before attempting I/O
        
        Loading behavior contract:
            - document_id: Should be unique and stable for same source
            - file_name: Should be human-readable (use basename, not full path)
            - content: Should be fully loaded into memory as string
            - Encoding: Should use UTF-8 by default, detect or configure if needed
            - Line endings: May normalize \r\n to \n (platform-specific)
            - BOM: Should handle and strip UTF-8 BOM if present
        
        Edge cases to handle:
            - Empty files: Return Document with empty content (not error)
            - Binary files: Should raise DocumentLoadException with clear message
            - Very large files: May warn or fail if exceeds reasonable limit
            - Non-existent paths: Raise DocumentLoadException immediately
            - Directories: Raise DocumentLoadException (not a file)
            - Symbolic links: Should follow and validate target
            - Permission errors: Raise DocumentLoadException with clear cause
        
        Encoding handling:
            - Default: UTF-8 encoding assumed
            - Fallback: May attempt other encodings (Latin-1, etc.) if configured
            - Detection: May use charset detection libraries
            - Errors: UnicodeDecodeError should be wrapped in DocumentLoadException
            - BOM: Handle UTF-8/UTF-16 BOM markers appropriately
        
        Security considerations:
            - Path traversal: Should validate or sanitize paths to prevent ../.. attacks
            - File size limits: Should enforce reasonable size limits
            - Timeout: Network loaders should timeout appropriately
            - Validation: Should validate file type if extension restrictions configured
        
        Performance considerations:
            - Should complete within reasonable time (<1s for local files)
            - May cache or pool connections for remote sources
            - Large files should warn or fail fast if unsupported
            - Should not hold file handles open longer than necessary
        
        Example:
            >>> loader = DocumentLoader(encoding="utf-8")
            >>> document = loader.load("documents/example.txt")
            >>> print(f"Loaded: {document.file_name}")
            >>> print(f"Content length: {len(document.content)} chars")
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement load() method"
        )