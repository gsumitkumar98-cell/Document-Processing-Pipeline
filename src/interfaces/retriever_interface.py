from abc import ABC, abstractmethod

from src.models.chunk import Chunk
from src.models.retrieval_result import RetrievalResult


class RetrieverInterface(ABC):
    """
    Abstract interface for document chunk retrieval implementations.
    
    Defines the contract for searching and ranking document chunks based on queries.
    Implementations must provide relevance scoring and result ordering.
    
    Design principles:
    - Stateless operation: retrieve() should not modify instance or input state
    - Scoring transparency: Results include explicit scores for debugging
    - Robustness: Must handle edge cases gracefully (empty inputs, malformed data)
    - Performance awareness: Should scale reasonably with chunk collection size
    
    Common implementations:
    - Keyword/lexical retrieval (BM25, TF-IDF)
    - Semantic retrieval (embedding similarity)
    - Hybrid retrieval (combining multiple signals)
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        chunks: list[Chunk]
    ) -> list[RetrievalResult]:
        """
        Retrieve and rank chunks relevant to the query.
        
        Searches the provided chunk collection and returns results ranked by
        relevance score in descending order (most relevant first).
        
        Args:
            query: Search query string
                - Must be non-empty after stripping whitespace
                - Should be validated for minimum length (typically 2+ chars)
                - Case handling is implementation-specific
                
            chunks: Collection of Chunk objects to search
                - Must be a list (or compatible sequence)
                - Can be empty (returns empty results)
                - Each chunk must have valid text attribute
                - Duplicates are allowed; implementation handles deduplication if needed
        
        Returns:
            List of RetrievalResult objects, each containing:
                - score: Numeric relevance score (higher = more relevant)
                - chunk: Reference to the matched Chunk object
            
            Results are ordered by descending score (highest first).
            Empty list returned if no matches found.
            Never returns None.
        
        Raises:
            ValueError: If query is None, empty, or too short after validation
            TypeError: If query is not a string or chunks is not a list
            RetrievalException: If retrieval operation fails (malformed chunks, 
                               scoring errors, or implementation-specific issues)
        
        Input validation requirements:
            - Query: Must validate type (str), emptiness, and minimum length
            - Chunks: Must validate type (list), and optionally validate each 
                     chunk has required attributes (text, document_id, etc.)
            - Should log warnings for skipped/invalid chunks rather than failing
        
        Scoring contract:
            - Scores must be non-negative floats
            - Score 0 indicates no relevance (typically filtered from results)
            - Score magnitude is implementation-specific (not normalized)
            - Consistent ordering: higher score always means more relevant
        
        Edge cases to handle:
            - Empty query after stripping: Raise ValueError
            - Empty chunks list: Return empty list (not an error)
            - Query with no matches: Return empty list
            - Malformed chunk (missing text): Log warning, skip chunk
            - Duplicate chunks: Include all unless deduplication implemented
            - Very large chunk collections: Should not fail, may warn on performance
        
        Performance considerations:
            - Should handle 1000+ chunks within reasonable time (<1s typical)
            - May implement result limiting or pagination for very large results
            - Should avoid loading entire corpus into memory if possible
        
        Example:
            >>> retriever = KeywordRetriever()
            >>> results = retriever.retrieve("python programming", chunks)
            >>> for result in results[:5]:  # Top 5 results
            ...     print(f"Score: {result.score}, Text: {result.chunk.text[:50]}")
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement retrieve() method"
        )