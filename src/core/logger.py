import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from pythonjsonlogger import jsonlogger

from src.core.config import settings


def get_logger(
    logger_name: str,
    log_dir: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Get or create a configured logger instance with JSON formatting.
    
    Creates a logger with both file and console handlers using JSON format.
    File handler uses rotation to manage log size. Logger configuration is
    cached per logger name to avoid duplicate handlers.
    
    Args:
        logger_name: Name for the logger (typically __name__ of calling module)
        log_dir: Directory for log files (default: "logs" or from environment)
        log_file: Log filename (default: "app.log")
        
    Returns:
        Configured Logger instance with JSON formatting and rotation
        
    Raises:
        OSError: If log directory cannot be created
        PermissionError: If insufficient permissions to write logs
        
    Logger configuration:
        - Level: From settings.LOG_LEVEL (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - Format: JSON with timestamp, level, logger name, and message
        - File handler: Rotating with 1MB max size, 5 backup files
        - Console handler: Outputs to stderr with same JSON format
        - Propagation: Disabled to prevent duplicate logs
        
    File rotation:
        - Max file size: 1 MB per file
        - Backup count: 5 files (app.log, app.log.1, ..., app.log.5)
        - Total max storage: ~6 MB
        - Rotation strategy: Oldest backup deleted when limit reached
        
    Caching behavior:
        - Logger instances are cached by Python's logging module
        - If logger already has handlers, returns existing instance
        - Prevents duplicate handler registration on repeated calls
        
    Concurrency notes:
        - RotatingFileHandler is NOT process-safe
        - In multi-process deployments (gunicorn, celery), consider:
          * Using QueueHandler with centralized logging process
          * External log aggregation (CloudWatch, Elasticsearch)
          * Process-specific log files with PID suffix
        - Thread-safe within single process
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started", extra={"document_id": "doc123"})
        >>> logger.error("Failed to load", extra={"error": str(e)})
    """
    # Resolve log directory from config or parameter
    if log_dir is None:
        # Use Path from settings, convert to string
        log_dir_path = getattr(settings, 'LOG_DIR', Path("logs"))
        if isinstance(log_dir_path, str):
            log_dir_path = Path(log_dir_path)
        log_dir = str(log_dir_path)
    
    if log_file is None:
        log_file = getattr(settings, 'LOG_FILE', "app.log")
    
    # Get or create logger
    logger = logging.getLogger(logger_name)
    
    # Return cached logger if already configured
    if logger.handlers:
        return logger
    
    # Set log level from settings
    try:
        log_level = getattr(logging, settings.LOG_LEVEL.upper())
        logger.setLevel(log_level)
    except AttributeError:
        # Fallback to INFO if invalid level in settings
        logger.setLevel(logging.INFO)
        logger.warning(
            f"Invalid LOG_LEVEL '{settings.LOG_LEVEL}', defaulting to INFO"
        )
    
    # Create log directory with error handling
    try:
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(
            f"Cannot create log directory '{log_dir}': Permission denied"
        ) from e
    except OSError as e:
        raise OSError(
            f"Cannot create log directory '{log_dir}': {e}"
        ) from e
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    
    # Create and configure file handler with error handling
    try:
        log_file_path = log_dir_path / log_file
        file_handler = RotatingFileHandler(
            filename=str(log_file_path),
            maxBytes=1024 * 1024,  # 1 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # Capture all levels in file
        logger.addHandler(file_handler)
        
    except (PermissionError, OSError) as e:
        # Log to console if file handler fails
        logger.warning(
            f"Could not create file handler for {log_file_path}: {e}. "
            "Logging to console only."
        )
    
    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)  # Less verbose on console
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def configure_root_logger() -> None:
    """
    Configure the root logger for application-wide logging.
    
    Should be called once at application startup. Useful for catching
    logs from third-party libraries.
    """
    root_logger = logging.getLogger()
    
    # Avoid reconfiguring if already set up
    if root_logger.handlers:
        return
    
    root_logger.setLevel(logging.WARNING)  # Only warnings and above from libs
    
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)