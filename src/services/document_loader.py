from pathlib import Path
from typing import Optional, List

from src.models.document import Document
from src.interfaces.document_loader_interface import DocumentLoaderInterface
from src.core.exceptions import DocumentLoadException
from src.core.logger import get_logger


logger = get_logger(__name__)


class DocumentLoader(DocumentLoaderInterface):
    """
    Loads text documents from the filesystem.
    
    Supports UTF-8 encoded text files with validation for file existence,
    type, permissions, and content readability.
    
    Attributes:
        encoding: Text encoding to use (default: utf-8)
        supported_extensions: List of allowed file extensions (None = all)
    """

    def __init__(
        self,
        encoding: str = "utf-8",
        supported_extensions: Optional[List[str]] = None
    ):
        """
        Initialize the document loader.
        
        Args:
            encoding: Text encoding for reading files (default: utf-8)
            supported_extensions: List of allowed extensions (e.g., ['.txt', '.md'])
                                 None means all extensions are allowed
        """
        self.encoding = encoding
        self.supported_extensions = supported_extensions

    def load(self, file_path: str) -> Document:
        """
        Load a document from the filesystem.
        
        Validates file existence, type, permissions, and content readability
        before creating a Document object.
        
        Args:
            file_path: Path to the document file (relative or absolute)
            
        Returns:
            Document object with file content and metadata
            
        Raises:
            DocumentLoadException: If file doesn't exist, is not readable, 
                                  or content cannot be decoded
            
        Validation steps:
            1. Check path is a string and not empty
            2. Check file exists
            3. Check path points to a regular file (not directory)
            4. Check file extension is supported (if restrictions configured)
            5. Check file is readable
            6. Attempt to decode content with specified encoding
            
        Edge cases:
            - Empty files: Returns Document with empty content string
            - Symbolic links: Follows links and validates target
            - Large files: No size limit imposed by this loader
        """
        # Validate file_path parameter
        if file_path is None:
            raise DocumentLoadException(
                message="File path cannot be None",
                details={"operation": "validate_path"}
            )
        
        if not isinstance(file_path, str):
            raise DocumentLoadException(
                message=f"File path must be a string, got {type(file_path).__name__}",
                file_path=str(file_path) if file_path else None,
                details={"path_type": type(file_path).__name__}
            )
        
        file_path = file_path.strip()
        if not file_path:
            raise DocumentLoadException(
                message="File path cannot be empty or whitespace",
                details={"operation": "validate_path"}
            )

        logger.info(f"Loading document from: {file_path}")

        try:
            path = Path(file_path)
            
            # Check if path exists
            if not path.exists():
                raise DocumentLoadException(
                    message=f"File does not exist",
                    file_path=file_path,
                    details={"operation": "check_existence"}
                )
            
            # Check if path is a regular file (not directory, symlink to directory, etc.)
            if not path.is_file():
                if path.is_dir():
                    error_type = "directory"
                elif path.is_symlink():
                    error_type = "broken_symlink"
                else:
                    error_type = "special_file"
                
                raise DocumentLoadException(
                    message=f"Path is not a regular file ({error_type})",
                    file_path=file_path,
                    details={"path_type": error_type, "operation": "validate_file_type"}
                )
            
            # Check file extension if restrictions are configured
            if self.supported_extensions is not None:
                if path.suffix.lower() not in self.supported_extensions:
                    raise DocumentLoadException(
                        message=f"Unsupported file extension: {path.suffix}",
                        file_path=file_path,
                        details={
                            "extension": path.suffix,
                            "supported": self.supported_extensions,
                            "operation": "validate_extension"
                        }
                    )
            
            # Attempt to read file content with encoding
            try:
                content = path.read_text(encoding=self.encoding)
                file_size = path.stat().st_size
                
                logger.info(
                    f"Document loaded successfully",
                    extra={
                        "file": path.name,
                        "size_bytes": file_size,
                        "content_length": len(content),
                        "encoding": self.encoding
                    }
                )
                
            except PermissionError as e:
                raise DocumentLoadException(
                    message="Permission denied reading file",
                    file_path=file_path,
                    details={"operation": "read_file"},
                    original_exception=e
                )
            
            except UnicodeDecodeError as e:
                raise DocumentLoadException(
                    message=f"Failed to decode file with {self.encoding} encoding",
                    file_path=file_path,
                    details={
                        "encoding": self.encoding,
                        "operation": "decode_content",
                        "error_position": f"byte {e.start}" if hasattr(e, 'start') else "unknown"
                    },
                    original_exception=e
                )
            
            except OSError as e:
                raise DocumentLoadException(
                    message=f"OS error reading file: {e.strerror if hasattr(e, 'strerror') else str(e)}",
                    file_path=file_path,
                    details={"operation": "read_file", "errno": e.errno if hasattr(e, 'errno') else None},
                    original_exception=e
                )

            # Create and return Document object
            return Document(
                document_id=str(path.resolve()),  # Use absolute path as ID
                file_name=path.name,
                content=content
            )

        except DocumentLoadException:
            # Re-raise our custom exceptions without wrapping
            raise
        
        except Exception as error:
            # Wrap unexpected errors with context
            logger.exception(
                f"Unexpected error loading document: {error}",
                extra={"file_path": file_path}
            )
            raise DocumentLoadException(
                message=f"Unexpected error loading document: {str(error)}",
                file_path=file_path,
                details={
                    "error_type": type(error).__name__,
                    "operation": "load_document"
                },
                original_exception=error
            )