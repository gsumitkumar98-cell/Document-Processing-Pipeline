from fastapi import FastAPI

from src.core.config import settings

from src.dependency.container import (
    get_pipeline_service
)

from src.utils.file_helper import (
    get_document_files
)

app = FastAPI(
    title=settings.APP_NAME
)

pipeline = get_pipeline_service()

files = get_document_files(
    settings.DOCUMENT_PATH
)

pipeline.process_documents(
    files
)


@app.get("/")
def health_check():

    return {
        "message": "Document Processing Pipeline Running"
    }


@app.get("/search")
def search(
    query: str
):

    response = pipeline.search(
        query
    )

    return {
        "query": response.query,
        "total_results":
            response.total_results,
        "results": [
            {
                "document":
                    chunk.document_name,
                "chunk_id":
                    chunk.chunk_id,
                "text":
                    chunk.text
            }
            for chunk in response.chunks
        ]
    }