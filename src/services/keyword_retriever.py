from typing import List
import re
from collections import Counter

from src.models.chunk import Chunk
from src.models.retrieval_result import RetrievalResult
from src.interfaces.retriever_interface import RetrieverInterface
from src.core.logger import get_logger
from src.core.exceptions import RetrievalException


logger = get_logger(__name__)


class KeywordRetriever(RetrieverInterface):
    """
    Keyword-based retrieval using TF (term frequency) scoring.
    
    Matches query terms against chunk text and ranks results by relevance.
    Uses normalized tokenization with punctuation handling and optional
    case-insensitive matching.
    
    Scoring:
    - Term Frequency: Number of query term occurrences in chunk
    - Normalization: Removes punctuation, converts to lowercase
    - Ranking: Chunks sorted by descending score
    
    Attributes:
        case_sensitive: Whether to match terms case-sensitively (default: False)
        min_score: Minimum score threshold for results (default: 0, returns all matches)
    """

    def __init__(self, case_sensitive: bool = False, min_score: float = 0.0):
        """
        Initialize the keyword retriever.
        
        Args:
            case_sensitive: Whether to perform case-sensitive matching
            min_score: Minimum score threshold for including results (>= 0)
            
        Raises:
            ValueError: If min_score is negative
        """
        if not isinstance(min_score, (int, float)):
            raise ValueError(f"min_score must be numeric, got {type(min_score).__name__}")
        
        if min_score < 0:
            raise ValueError(f"min_score must be non-negative, got {min_score}")

        self.case_sensitive = case_sensitive
        self.min_score = min_score

    def _normalize_text(self, text: str) -> List[str]:
        """
        Normalize text by removing punctuation and tokenizing.
        
        Args:
            text: Input text to normalize
            
        Returns:
            List of normalized tokens
        """
        # Remove punctuation and split on whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Convert to lowercase if not case-sensitive
        if not self.case_sensitive:
            text = text.lower()
        
        # Split and filter empty tokens
        tokens = [token.strip() for token in text.split() if token.strip()]
        return tokens

    def retrieve(
        self,
        query: str,
        chunks: List[Chunk]
    ) -> List[RetrievalResult]:
        """
        Retrieve and rank chunks matching the query.
        
        Scores each chunk based on term frequency of query words.
        Returns results sorted by descending score.
        
        Args:
            query: Search query string
            chunks: List of Chunk objects to search
            
        Returns:
            List of RetrievalResult objects sorted by score (highest first)
            Returns empty list if no matches found
            
        Raises:
            RetrievalException: If validation fails or retrieval encounters errors
            
        Scoring details:
            - Each query term occurrence in chunk adds to score
            - Repeated terms count multiple times (term frequency)
            - Chunks with score <= min_score are filtered out
            
        Edge cases:
            - Empty query: raises ValueError
            - Empty chunks list: returns empty results
            - Chunks with empty/None text: logged as warning, skipped
        """
        # Validate query
        if query is None:
            raise RetrievalException(
                message="Query cannot be None",
                query=None,
                details={"operation": "validate_query"}
            )
        
        if not isinstance(query, str):
            raise RetrievalException(
                message=f"Query must be a string, got {type(query).__name__}",
                query=str(query) if query else None,
                details={"query_type": type(query).__name__}
            )
        
        query = query.strip()
        if not query:
            raise RetrievalException(
                message="Query cannot be empty or whitespace",
                query="",
                details={"operation": "validate_query"}
            )

        # Validate chunks
        if chunks is None:
            raise RetrievalException(
                message="Chunks list cannot be None",
                query=query,
                details={"operation": "validate_chunks"}
            )
        
        if not isinstance(chunks, list):
            raise RetrievalException(
                message=f"Chunks must be a list, got {type(chunks).__name__}",
                query=query,
                details={"chunks_type": type(chunks).__name__}
            )

        logger.info(
            f"Starting retrieval",
            extra={
                "query": query,
                "total_chunks": len(chunks),
                "case_sensitive": self.case_sensitive,
                "min_score": self.min_score
            }
        )

        try:
            # Normalize and tokenize query
            query_tokens = self._normalize_text(query)
            
            if not query_tokens:
                logger.warning(
                    f"Query produced no tokens after normalization",
                    extra={"query": query}
                )
                return []

            query_term_counts = Counter(query_tokens)
            logger.info(
                f"Query normalized to {len(query_tokens)} tokens ({len(query_term_counts)} unique)",
                extra={"query_tokens": query_tokens}
            )

            results = []
            skipped_chunks = 0

            for idx, chunk in enumerate(chunks):
                # Validate chunk object
                if not isinstance(chunk, Chunk):
                    logger.warning(
                        f"Skipping non-Chunk object at index {idx}: {type(chunk).__name__}"
                    )
                    skipped_chunks += 1
                    continue

                # Validate chunk text
                if not hasattr(chunk, 'text') or chunk.text is None:
                    logger.warning(
                        f"Skipping chunk with None text",
                        extra={
                            "chunk_id": getattr(chunk, 'chunk_id', 'unknown'),
                            "document": getattr(chunk, 'document_name', 'unknown')
                        }
                    )
                    skipped_chunks += 1
                    continue

                if not isinstance(chunk.text, str):
                    logger.warning(
                        f"Skipping chunk with non-string text: {type(chunk.text).__name__}",
                        extra={
                            "chunk_id": getattr(chunk, 'chunk_id', 'unknown'),
                            "document": getattr(chunk, 'document_name', 'unknown')
                        }
                    )
                    skipped_chunks += 1
                    continue

                # Handle empty chunk text
                if not chunk.text.strip():
                    logger.debug(
                        f"Skipping chunk with empty text",
                        extra={
                            "chunk_id": getattr(chunk, 'chunk_id', 'unknown'),
                            "document": getattr(chunk, 'document_name', 'unknown')
                        }
                    )
                    skipped_chunks += 1
                    continue

                # Normalize chunk text and calculate score
                chunk_tokens = self._normalize_text(chunk.text)
                chunk_term_counts = Counter(chunk_tokens)
                
                # Calculate term frequency score
                score = sum(
                    min(query_term_counts[term], chunk_term_counts[term])
                    for term in query_term_counts
                )

                # Only include chunks above threshold
                if score > self.min_score:
                    results.append(
                        RetrievalResult(
                            score=float(score),
                            chunk=chunk
                        )
                    )

            # Sort by score descending
            results.sort(key=lambda r: r.score, reverse=True)

            logger.info(
                f"Retrieval completed",
                extra={
                    "query": query,
                    "total_results": len(results),
                    "skipped_chunks": skipped_chunks,
                    "top_score": results[0].score if results else 0
                }
            )

            return results

        except RetrievalException:
            # Re-raise our custom exceptions
            raise
        except Exception as error:
            # Wrap unexpected errors with rich context
            logger.exception(
                f"Unexpected error during retrieval: {error}",
                extra={"query": query, "chunk_count": len(chunks) if chunks else 0}
            )
            raise RetrievalException(
                message=f"Unexpected error during retrieval: {str(error)}",
                query=query,
                details={
                    "chunk_count": len(chunks) if chunks else 0,
                    "error_type": type(error).__name__
                },
                original_exception=error
            )