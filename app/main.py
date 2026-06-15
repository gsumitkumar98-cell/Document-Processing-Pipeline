from fastapi import (
    FastAPI,
    Request,
    Query,
    HTTPException
)

from pydantic import BaseModel, Field
from typing import List

import logging

from src.core.config import settings

from src.dependency.container import (
    get_pipeline_service
)

from src.utils.file_helper import (
    get_document_files
)

logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Search query"
    )


class ChunkResponse(BaseModel):
    document: str
    chunk_id: int
    text: str


class SearchResponse(BaseModel):
    query: str
    total_results: int
    chunks: List[ChunkResponse]

app = FastAPI(
    title=settings.APP_NAME
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize and index documents when the application starts.
    """

    try:

        pipeline = get_pipeline_service()

        files = get_document_files(
            settings.DOCUMENT_PATH
        )

        pipeline.process_documents(
            files
        )

        app.state.pipeline = pipeline

        logger.info(
            "Pipeline initialized successfully"
        )

    except Exception:

        logger.exception(
            "Pipeline initialization failed"
        )

        raise


@app.get("/")
def health_check():

    return {
        "message": "Document Processing Pipeline Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.get(
    "/search",
    response_model=SearchResponse
)
def search(
    request: Request,
    query: str = Query(
        ...,
        min_length=2,
        max_length=500,
        description="Search query"
    )
):
    """
    Search indexed documents.
    """

    try:

        pipeline = request.app.state.pipeline

        response = pipeline.search(
            query
        )

        return {
            "query": response.query,
            "total_results": response.total_results,
            "chunks": [
                {
                    "document": chunk.document_name,
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text
                }
                for chunk in response.chunks
            ]
        }

    except ValueError as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )

    except Exception:

        logger.exception(
            "Search operation failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )