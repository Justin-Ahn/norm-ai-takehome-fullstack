from fastapi import FastAPI, Query
from app.utils import Output
from app.utils import DocumentService, PDFPosition

doc_serivce = DocumentService(
    filepath="docs/laws.pdf",
    parse_start=PDFPosition(page_number=0, y_coord=80),
    parse_end=PDFPosition(page_number=1, y_coord=640),
)
docs = doc_serivce.create_documents()
print(docs)
app = FastAPI()

"""
Please create an endpoint that accepts a query string, e.g., "what happens if I steal 
from the Sept?" and returns a JSON response serialized from the Pydantic Output class.
"""
