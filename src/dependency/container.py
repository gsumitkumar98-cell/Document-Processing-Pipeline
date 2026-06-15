from typing import Optional
from functools import lru_cache

from src.core.config import settings, get_settings
from src.core.logger import get_logger
from src.core.exceptions import PipelineException

from src.repositories.chunk_repository import ChunkRepository
from src.services.document_loader import DocumentLoader
from src.services.text_chunker import TextChunker
from src.services.keyword_retriever import KeywordRetriever
from src.services.pipeline_service import PipelineService

from src.interfaces.repository_interface import RepositoryInterface
from src.interfaces.document_loader_interface import DocumentLoaderInterface
from src.interfaces.chunker_interface import ChunkerInterface
from src.interfaces.retriever_interface import RetrieverInterface


logger = get_logger(__name__)


class DependencyContainer:
    """
    Dependency injection container for application services.
    
    Manages creation and wiring of service dependencies with support for
    testing overrides, lifecycle management, and configuration validation.
    
    Design patterns:
        - Factory pattern: Creates service instances on demand
        - Dependency injection: Wires dependencies through constructors
        - Override pattern: Allows test doubles and alternate implementations
        
    Features:
        - Configuration validation before instantiation
        - Graceful error handling with detailed diagnostics
        - Support for dependency overrides (testing, alternate backends)
        - Lazy initialization with caching
        - Clear separation of interfaces and implementations
    """

    def __init__(self):
        """Initialize container with default (no overrides)."""
        self._loader_override: Optional[DocumentLoaderInterface] = None
        self._chunker_override: Optional[ChunkerInterface] = None
        self._repository_override: Optional[RepositoryInterface] = None
        self._retriever_override: Optional[RetrieverInterface] = None

    def override_loader(self, loader: DocumentLoaderInterface) -> None:
        """Override document loader implementation for testing."""
        self._loader_override = loader
        logger.info(f"Loader overridden with {type(loader).__name__}")

    def override_chunker(self, chunker: ChunkerInterface) -> None:
        """Override chunker implementation for testing."""
        self._chunker_override = chunker
        logger.info(f"Chunker overridden with {type(chunker).__name__}")

    def override_repository(self, repository: RepositoryInterface) -> None:
        """Override repository implementation for testing."""
        self._repository_override = repository
        logger.info(f"Repository overridden with {type(repository).__name__}")

    def override_retriever(self, retriever: RetrieverInterface) -> None:
        """Override retriever implementation for testing."""
        self._retriever_override = retriever
        logger.info(f"Retriever overridden with {type(retriever).__name__}")

    def reset_overrides(self) -> None:
        """Clear all overrides, reverting to default implementations."""
        self._loader_override = None
        self._chunker_override = None
        self._repository_override = None
        self._retriever_override = None
        logger.info("All dependency overrides cleared")

    def get_loader(self) -> DocumentLoaderInterface:
        """Get document loader instance with validated configuration."""
        if self._loader_override:
            return self._loader_override
        
        try:
            encoding = getattr(settings, 'DOCUMENT_ENCODING', 'utf-8')
            loader = DocumentLoader(encoding=encoding)
            logger.debug(f"Created DocumentLoader with encoding={encoding}")
            return loader
        except Exception as e:
            logger.error(f"Failed to create DocumentLoader: {e}")
            raise PipelineException(
                message="Failed to initialize document loader",
                operation="dependency_injection",
                details={"component": "DocumentLoader", "error": str(e)},
                original_exception=e
            )

    def get_chunker(self) -> ChunkerInterface:
        """Get text chunker instance with validated configuration."""
        if self._chunker_override:
            return self._chunker_override
        
        try:
            chunk_size = settings.CHUNK_SIZE
            
            if not isinstance(chunk_size, int) or chunk_size <= 0:
                raise ValueError(f"CHUNK_SIZE must be positive integer, got {chunk_size}")
            
            if chunk_size > 10000:
                logger.warning(f"CHUNK_SIZE is very large ({chunk_size})")
            
            overlap = getattr(settings, 'CHUNK_OVERLAP', 0)
            chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)
            logger.debug(f"Created TextChunker with chunk_size={chunk_size}, overlap={overlap}")
            return chunker
        except Exception as e:
            logger.error(f"Failed to create TextChunker: {e}")
            raise PipelineException(
                message="Failed to initialize text chunker",
                operation="dependency_injection",
                details={"component": "TextChunker", "error": str(e)},
                original_exception=e
            )

    def get_repository(self) -> RepositoryInterface:
        """Get chunk repository instance."""
        if self._repository_override:
            return self._repository_override
        
        try:
            repository = ChunkRepository()
            logger.debug("Created ChunkRepository")
            return repository
        except Exception as e:
            logger.error(f"Failed to create ChunkRepository: {e}")
            raise PipelineException(
                message="Failed to initialize chunk repository",
                operation="dependency_injection",
                details={"component": "ChunkRepository", "error": str(e)},
                original_exception=e
            )

    def get_retriever(self) -> RetrieverInterface:
        """Get retriever instance with validated configuration."""
        if self._retriever_override:
            return self._retriever_override
        
        try:
            case_sensitive = getattr(settings, 'RETRIEVER_CASE_SENSITIVE', False)
            min_score = getattr(settings, 'RETRIEVER_MIN_SCORE', 0.0)
            
            retriever = KeywordRetriever(case_sensitive=case_sensitive, min_score=min_score)
            logger.debug(f"Created KeywordRetriever")
            return retriever
        except Exception as e:
            logger.error(f"Failed to create KeywordRetriever: {e}")
            raise PipelineException(
                message="Failed to initialize retriever",
                operation="dependency_injection",
                details={"component": "KeywordRetriever", "error": str(e)},
                original_exception=e
            )

    def get_pipeline_service(self) -> PipelineService:
        """
        Get fully wired pipeline service.
        
        Creates and wires all dependencies with validated configuration.
        
        Returns:
            PipelineService instance with all dependencies injected
            
        Raises:
            PipelineException: If any dependency fails to initialize
        """
        try:
            loader = self.get_loader()
            chunker = self.get_chunker()
            repository = self.get_repository()
            retriever = self.get_retriever()
            
            pipeline = PipelineService(
                loader=loader,
                chunker=chunker,
                repository=repository,
                retriever=retriever
            )
            
            logger.info("PipelineService initialized successfully")
            return pipeline
        except PipelineException:
            raise
        except Exception as e:
            logger.error(f"Failed to create PipelineService: {e}")
            raise PipelineException(
                message="Failed to initialize pipeline service",
                operation="dependency_injection",
                details={"error": str(e)},
                original_exception=e
            )


# Global container instance
_container = DependencyContainer()


def get_container() -> DependencyContainer:
    """
    Get global dependency container instance.
    
    Returns singleton container for dependency management.
    For testing, use container.override_* methods or create new container.
    
    Returns:
        Global DependencyContainer instance
    """
    return _container


def get_pipeline_service() -> PipelineService:
    """
    Get pipeline service from global container.
    
    Convenience function for retrieving fully configured pipeline.
    Maintains backward compatibility with existing code.
    
    Returns:
        PipelineService instance
    """
    return _container.get_pipeline_service()
