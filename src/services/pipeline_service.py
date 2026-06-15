from typing import List, Optional

from src.models.search_response import SearchResponse
from src.models.retrieval_result import RetrievalResult
from src.interfaces.document_loader_interface import DocumentLoaderInterface
from src.interfaces.chunker_interface import ChunkerInterface
from src.interfaces.repository_interface import RepositoryInterface
from src.interfaces.retriever_interface import RetrieverInterface
from src.core.logger import get_logger
from src.core.exceptions import (
    PipelineException,
    DocumentLoadException,
    ChunkingException,
    RepositoryException,
    RetrievalException
)


logger = get_logger(__name__)


class PipelineService:
    """
    Orchestrates document processing pipeline including loading, chunking, storage, and retrieval.
    
    This service coordinates the document processing workflow:
    1. Load documents from file paths
    2. Chunk documents into smaller segments
    3. Store chunks in repository
    4. Retrieve relevant chunks based on search queries
    
    Attributes:
        loader: Document loader implementation
        chunker: Text chunker implementation
        repository: Chunk storage repository
        retriever: Search/retrieval implementation
    """

    def __init__(
        self,
        loader: DocumentLoaderInterface,
        chunker: ChunkerInterface,
        repository: RepositoryInterface,
        retriever: RetrieverInterface
    ):
        if not loader:
            raise ValueError("Loader cannot be None")
        if not chunker:
            raise ValueError("Chunker cannot be None")
        if not repository:
            raise ValueError("Repository cannot be None")
        if not retriever:
            raise ValueError("Retriever cannot be None")

        self.loader = loader
        self.chunker = chunker
        self.repository = repository
        self.retriever = retriever

    def process_documents(
        self,
        files: List[str],
        clear_existing: bool = True
    ) -> None:
        """
        Process multiple document files through the pipeline.
        
        Loads, chunks, and stores documents. By default, clears existing repository
        data before processing to ensure a clean state.
        
        Args:
            files: List of file paths to process
            clear_existing: Whether to clear repository before processing (default: True)
            
        Raises:
            ValueError: If files is None, empty, or contains invalid paths
            PipelineException: If processing fails at any stage
            
        Side effects:
            - Clears repository if clear_existing=True
            - Adds all successfully processed chunks to repository
            - Logs progress and errors
        """
        if files is None:
            raise ValueError("Files list cannot be None")
        
        if not isinstance(files, list):
            raise ValueError("Files must be a list of file paths")
        
        if not files:
            raise ValueError("Files list cannot be empty")
        
        # Validate all file paths are strings and non-empty
        for idx, file_path in enumerate(files):
            if not isinstance(file_path, str):
                raise ValueError(f"File path at index {idx} must be a string, got {type(file_path).__name__}")
            if not file_path.strip():
                raise ValueError(f"File path at index {idx} cannot be empty or whitespace")

        if clear_existing:
            logger.info("Clearing existing repository data")
            self.repository.clear()

        total_chunks = 0
        processed_files = 0
        failed_files = []

        logger.info(f"Starting document processing for {len(files)} files")

        for file_path in files:
            try:
                logger.info(f"Processing file: {file_path}")
                
                # Load document with error handling
                try:
                    document = self.loader.load(file_path)
                except Exception as e:
                    raise DocumentLoadException(
                        message=f"Failed to load document",
                        file_path=file_path,
                        original_exception=e
                    )

                # Chunk document with error handling
                try:
                    chunks = self.chunker.chunk(document)
                    chunk_count = len(chunks) if chunks else 0
                    logger.info(f"Created {chunk_count} chunks from {file_path}")
                except Exception as e:
                    raise ChunkingException(
                        message=f"Failed to chunk document",
                        document_id=document.document_id if document else None,
                        details={"file_path": file_path},
                        original_exception=e
                    )

                # Store chunks with error handling
                try:
                    self.repository.add_chunks(chunks)
                    total_chunks += chunk_count
                    processed_files += 1
                except Exception as e:
                    raise RepositoryException(
                        message=f"Failed to store chunks",
                        details={"file_path": file_path, "chunk_count": chunk_count},
                        original_exception=e
                    )

            except (DocumentLoadException, ChunkingException, RepositoryException) as e:
                logger.error(f"Failed to process {file_path}: {e}")
                failed_files.append({"file": file_path, "error": str(e)})
            except Exception as e:
                logger.error(f"Unexpected error processing {file_path}: {e}")
                failed_files.append({"file": file_path, "error": f"Unexpected error: {str(e)}"})

        # Log summary
        logger.info(
            f"Document processing completed: {processed_files}/{len(files)} files processed, "
            f"{total_chunks} total chunks stored"
        )

        if failed_files:
            logger.warning(f"Failed to process {len(failed_files)} files: {failed_files}")
            raise PipelineException(
                message=f"Processing completed with {len(failed_files)} failures",
                operation="process_documents",
                details={"failed_files": failed_files, "success_count": processed_files}
            )

    def search(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> SearchResponse:
        """
        Search for relevant document chunks matching the query.
        
        Args:
            query: Search query string
            max_results: Optional limit on number of results (default: None for unlimited)
            
        Returns:
            SearchResponse containing query, result count, and matching chunks
            
        Raises:
            ValueError: If query is None, empty, or invalid
            RetrievalException: If search operation fails
        """
        # Validate query
        if query is None:
            raise ValueError("Query cannot be None")
        
        if not isinstance(query, str):
            raise ValueError(f"Query must be a string, got {type(query).__name__}")
        
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty or whitespace")
        
        if len(query) < 2:
            raise ValueError("Query must be at least 2 characters long")
        
        if max_results is not None and (not isinstance(max_results, int) or max_results <= 0):
            raise ValueError("max_results must be a positive integer")

        logger.info(f"Starting search for query: '{query}'")

        try:
            # Retrieve all chunks from repository
            try:
                chunks = self.repository.get_chunks()
                logger.info(f"Retrieved {len(chunks)} chunks from repository")
            except Exception as e:
                raise RepositoryException(
                    message="Failed to retrieve chunks from repository",
                    original_exception=e
                )

            # Perform retrieval
            try:
                results: List[RetrievalResult] = self.retriever.retrieve(query, chunks)
                logger.info(f"Retrieval returned {len(results)} results")
            except Exception as e:
                raise RetrievalException(
                    message="Failed to retrieve matching chunks",
                    query=query,
                    details={"chunk_count": len(chunks)},
                    original_exception=e
                )

            # Apply max_results limit if specified
            if max_results is not None:
                results = results[:max_results]
                logger.info(f"Limited results to {max_results}")

            response = SearchResponse(
                query=query,
                total_results=len(results),
                chunks=[result.chunk for result in results]
            )

            logger.info(f"Search completed: {response.total_results} results for query '{query}'")
            return response

        except (RepositoryException, RetrievalException) as e:
            logger.error(f"Search failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise PipelineException(
                message="Unexpected error during search operation",
                operation="search",
                details={"query": query},
                original_exception=e
            )