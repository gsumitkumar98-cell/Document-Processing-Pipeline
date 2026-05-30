from typing import List

from src.models.chunk import Chunk

from src.models.retrieval_result import (
    RetrievalResult
)

from src.interfaces.retriever_interface import (
    RetrieverInterface
)

from src.core.logger import get_logger

from src.core.exceptions import (
    RetrievalException
)


logger = get_logger(__name__)


class KeywordRetriever(
    RetrieverInterface
):

    def retrieve(
        self,
        query: str,
        chunks: List[Chunk]
    ) -> List[RetrievalResult]:

        try:

            query_words = set(
                query.lower().split()
            )

            results = []

            for chunk in chunks:

                chunk_words = set(
                    chunk.text.lower().split()
                )

                score = len(
                    query_words.intersection(
                        chunk_words
                    )
                )

                if score > 0:

                    results.append(
                        RetrievalResult(
                            score=float(score),
                            chunk=chunk
                        )
                    )

            results.sort(
                key=lambda result:
                result.score,
                reverse=True
            )

            logger.info(
                "Search completed",
                extra={
                    "query": query,
                    "results": len(results)
                }
            )

            return results

        except Exception as error:

            logger.exception(
                str(error)
            )

            raise RetrievalException(
                str(error)
            )