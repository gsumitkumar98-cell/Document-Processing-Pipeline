from pathlib import Path
from typing import Optional, List

from src.core.constants import SUPPORTED_EXTENSIONS
from src.core.exceptions import DocumentLoadException


def validate_document_path(
    file_path: str,
    allowed_extensions: Optional[List[str]] = None,
    check_readable: bool = True,
    max_size_mb: Optional[float] = None
) -> Path:
    """
    Validate document file path with comprehensive checks.
    
    Performs filesystem validation including existence, type, permissions,
    size, and extension checking. Returns validated Path object.
    
    Args:
        file_path: Path to document file (string)
        allowed_extensions: List of allowed extensions (e.g., ['.txt', '.md'])
                           If None, uses SUPPORTED_EXTENSIONS from constants
        check_readable: Whether to verify file is readable (default: True)
        max_size_mb: Maximum file size in MB (None = no limit)
        
    Returns:
        Validated Path object (absolute path)
        
    Raises:
        ValueError: If file_path is invalid (None, empty, wrong type)
        DocumentLoadException: If validation fails (not found, wrong type,
                              unreadable, too large, unsupported extension)
        
    Validation steps:
        1. Input validation (type, emptiness)
        2. Path resolution and existence check
        3. File type check (not directory, symlink target validation)
        4. Extension validation (if restrictions configured)
        5. Readability check (permissions)
        6. Size validation (if max_size_mb specified)
        
    Edge cases:
        - Symbolic links: Follows and validates target
        - Relative paths: Resolves to absolute
        - Case-insensitive extensions: Normalized to lowercase
        - Empty extension: Checked if in allowed list
        - Permission errors: Caught and wrapped with context
        
    Example:
        >>> path = validate_document_path("documents/example.txt")
        >>> print(path.absolute())
        >>> 
        >>> # With custom extensions
        >>> path = validate_document_path(
        ...     "data.json",
        ...     allowed_extensions=['.json', '.jsonl']
        ... )
    """
    # Input validation
    if file_path is None:
        raise ValueError("file_path cannot be None")
    
    if not isinstance(file_path, str):
        raise ValueError(
            f"file_path must be string, got {type(file_path).__name__}"
        )
    
    file_path = file_path.strip()
    if not file_path:
        raise ValueError("file_path cannot be empty or whitespace")
    
    # Convert to Path and resolve
    try:
        path = Path(file_path).resolve()
    except (OSError, RuntimeError) as e:
        raise DocumentLoadException(
            message=f"Invalid file path: {file_path}",
            file_path=file_path,
            details={"error": str(e), "operation": "path_resolution"},
            original_exception=e
        )
    
    # Check existence
    if not path.exists():
        raise DocumentLoadException(
            message=f"File does not exist",
            file_path=str(path),
            details={"operation": "check_existence"}
        )
    
    # Check if it's a regular file
    if not path.is_file():
        if path.is_dir():
            error_type = "directory"
        elif path.is_symlink():
            error_type = "broken_symlink"
        else:
            error_type = "special_file"
        
        raise DocumentLoadException(
            message=f"Path is not a regular file ({error_type})",
            file_path=str(path),
            details={"path_type": error_type, "operation": "validate_file_type"}
        )
    
    # Validate extension if restrictions configured
    extensions = allowed_extensions if allowed_extensions is not None else SUPPORTED_EXTENSIONS
    
    if extensions:
        file_extension = path.suffix.lower()
        normalized_extensions = [ext.lower() for ext in extensions]
        
        if file_extension not in normalized_extensions:
            raise DocumentLoadException(
                message=f"Unsupported file extension: {path.suffix}",
                file_path=str(path),
                details={
                    "extension": path.suffix,
                    "allowed": extensions,
                    "operation": "validate_extension"
                }
            )
    
    # Check readability
    if check_readable:
        try:
            # Attempt to open file in read mode
            with path.open('r', encoding='utf-8') as f:
                # Just verify we can open it, don't read content
                pass
        except PermissionError as e:
            raise DocumentLoadException(
                message="Permission denied: file is not readable",
                file_path=str(path),
                details={"operation": "check_readable"},
                original_exception=e
            )
        except UnicodeDecodeError:
            # File might be binary, but that's okay for this check
            # Actual loading will handle encoding issues
            pass
        except OSError as e:
            raise DocumentLoadException(
                message=f"Cannot read file: {e}",
                file_path=str(path),
                details={"operation": "check_readable"},
                original_exception=e
            )
    
    # Validate file size if limit specified
    if max_size_mb is not None:
        try:
            size_bytes = path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            if size_mb > max_size_mb:
                raise DocumentLoadException(
                    message=f"File too large: {size_mb:.2f}MB exceeds limit of {max_size_mb}MB",
                    file_path=str(path),
                    details={
                        "size_mb": size_mb,
                        "max_size_mb": max_size_mb,
                        "operation": "validate_size"
                    }
                )
        except OSError as e:
            raise DocumentLoadException(
                message=f"Cannot get file size: {e}",
                file_path=str(path),
                details={"operation": "check_size"},
                original_exception=e
            )
    
    return path


def validate_document(file_path: str) -> None:
    """
    Validate document file path (legacy function).
    
    Backward compatibility wrapper for validate_document_path.
    Validates using default settings from constants.
    
    Args:
        file_path: Path to document file
        
    Raises:
        ValueError: If file_path is invalid
        DocumentLoadException: If validation fails
    """
    validate_document_path(file_path)


def validate_query(
    query: str,
    min_length: int = 2,
    max_length: int = 500
) -> str:
    """
    Validate search query string.
    
    Checks query type, length constraints, and returns normalized query.
    
    Args:
        query: Search query string
        min_length: Minimum query length after stripping (default: 2)
        max_length: Maximum query length (default: 500)
        
    Returns:
        Normalized query (stripped whitespace)
        
    Raises:
        ValueError: If query is invalid (None, empty, wrong type, too short/long)
        
    Example:
        >>> query = validate_query("  python programming  ")
        >>> print(query)  # "python programming"
    """
    if query is None:
        raise ValueError("Query cannot be None")
    
    if not isinstance(query, str):
        raise ValueError(f"Query must be string, got {type(query).__name__}")
    
    query = query.strip()
    
    if not query:
        raise ValueError("Query cannot be empty or whitespace")
    
    if len(query) < min_length:
        raise ValueError(
            f"Query too short: {len(query)} chars, minimum is {min_length}"
        )
    
    if len(query) > max_length:
        raise ValueError(
            f"Query too long: {len(query)} chars, maximum is {max_length}"
        )
    
    return query


def validate_chunk_size(chunk_size: int, max_size: int = 10000) -> int:
    """
    Validate chunk size parameter.
    
    Args:
        chunk_size: Number of words/units per chunk
        max_size: Maximum allowed chunk size (default: 10000)
        
    Returns:
        Validated chunk size
        
    Raises:
        ValueError: If chunk_size is invalid
        
    Example:
        >>> size = validate_chunk_size(100)
        >>> print(size)  # 100
    """
    if not isinstance(chunk_size, int):
        raise ValueError(
            f"chunk_size must be integer, got {type(chunk_size).__name__}"
        )
    
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    
    if chunk_size > max_size:
        raise ValueError(
            f"chunk_size too large: {chunk_size}, maximum is {max_size}"
        )
    
    return chunk_size