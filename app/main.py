from fastapi import FastAPI, Query, HTTPException
from contextlib import asynccontextmanager
from app.utils import Output, DocumentService, PDFPosition, QdrantService, Input
from typing import Optional

qdrant_service: Optional[QdrantService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Move hard-coded configs into separate file/location
    doc_service = DocumentService(
        filepath="docs/laws.pdf",
        parse_start=PDFPosition(page_number=0, y_coord=80),
        parse_end=PDFPosition(page_number=1, y_coord=640),
    )
    docs = doc_service.create_documents()

    global qdrant_service
    qdrant_service = QdrantService(k=2)
    qdrant_service.connect()
    qdrant_service.load(docs)

    yield

    return


app = FastAPI(lifespan=lifespan)


@app.post("/v1/laws/game_of_thrones", response_model=Output)
def query_pdf(input_data: Input):
    assert qdrant_service

    try:
        response = qdrant_service.query(input_data.query)
        return response
    except Exception as e:
        print(f"Encountered exception while querying qdrant_service. Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
