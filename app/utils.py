from pydantic import BaseModel
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import Document, NodeRelationship, RelatedNodeInfo
from llama_index.core import (
    VectorStoreIndex,
    ServiceContext,
)
from dataclasses import dataclass
import pdfplumber
import re

# key = os.environ["OPENAI_API_KEY"]


@dataclass
class Input:
    query: str
    file_path: str


@dataclass
class Citation:
    source: str
    text: str


class Output(BaseModel):
    query: str
    response: str
    citations: list[Citation]


@dataclass
class PDFPosition:
    page_number: int
    y_coord: float


@dataclass
class LawSection:
    section_number: str
    section_title_or_content: str


class DocumentService:
    """
    Update this service to load the pdf and extract its contents.
    The example code below will help with the data structured required
    when using the QdrantService.load() method below. Note: for this
    exercise, ignore the subtle difference between llama-index's
    Document and Node classes (i.e, treat them as interchangeable).
    """

    def __init__(
        self, filepath: str, parse_start: PDFPosition, parse_end: PDFPosition
    ) -> None:
        self.filepath = filepath
        self.parse_start = parse_start
        self.parse_end = parse_end

    # Returns raw-lines of text from a PDF file, within the specified PDF positioning range
    def _extract_textlines_within_range(self, filepath: str) -> list[str]:
        with pdfplumber.open(filepath) as pdf:
            lines = []
            for i, page in enumerate(pdf.pages):
                y_top = 0
                y_bottom = page.height
                if i == self.parse_start.page_number:
                    y_top = self.parse_start.y_coord
                if i == self.parse_end.page_number:
                    y_bottom = self.parse_end.y_coord

                cropped = page.within_bbox((0, y_top, page.width, y_bottom))
                lines.extend(cropped.extract_text().splitlines())
            return lines

    NUMBERED_LIST_REGEX = "^(?P<number>(?:\\d+\\.)+)\\s+(?P<content>.+)$"

    # Takes in raw-lines of text from a PDF file and returns a string per each law section
    def _parse_lines_to_law_sections(self, lines: list[str]) -> list[LawSection]:
        # Merge all lines into one string per one law-section.
        law_section_lines = []
        for line in lines:
            if re.match(self.NUMBERED_LIST_REGEX, line):
                law_section_lines.append(line)
            else:
                law_section_lines[-1] = f"{law_section_lines[-1]} {line}"

        law_sections = []
        for line in law_section_lines:
            match = re.match(self.NUMBERED_LIST_REGEX, line)
            if not match:
                raise Exception(
                    f"Expected all lines to be well-formatted to be laws! Offending line: {line}"
                )
            section = match.group("number")
            content = match.group("content")
            law_sections.append(
                LawSection(section_number=section, section_title_or_content=content)
            )

        return law_sections

    # Apply node-relationships to provide better context for the LLM
    def _update_node_relationships(self, docs: list[Document]):
        section_to_doc = {doc.metadata["Section"]: doc for doc in docs}
        for section, doc in section_to_doc.items():
            match = re.match("(?P<parent>.+)(\\d\\.)+", section)
            if not match:
                continue

            if (parent_section := match.group("parent")) in section_to_doc:
                parent_doc = section_to_doc[parent_section]

                parent_doc.relationships[NodeRelationship.CHILD] = RelatedNodeInfo(
                    node_id=doc.node_id
                )
                doc.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(
                    node_id=parent_doc.node_id
                )

        for i in range(1, len(docs)):
            docs[i - 1].relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                node_id=docs[i].node_id
            )
            docs[i].relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                node_id=docs[i - 1].node_id
            )

    def create_documents(self) -> list[Document]:
        lines = self._extract_textlines_within_range(self.filepath)
        law_sections = self._parse_lines_to_law_sections(lines)
        docs = [
            Document(
                metadata={"Section": section.section_number},
                text=section.section_title_or_content,
            )
            for section in law_sections
        ]
        self._update_node_relationships(docs)

        return docs


class QdrantService:
    def __init__(self, k: int = 2):
        self.index = None
        self.k = k

    def connect(self) -> None:
        client = qdrant_client.QdrantClient(location=":memory:")

        vstore = QdrantVectorStore(client=client, collection_name="temp")

        service_context = ServiceContext.from_defaults(
            embed_model=OpenAIEmbedding(), llm=OpenAI(api_key=key, model="gpt-4")
        )

        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vstore, service_context=service_context
        )

    def load(self, docs: list[Document]):
        assert self.index is not None
        self.index.insert_nodes(docs)

    def query(self, query_str: str) -> Output:
        """
        This method needs to initialize the query engine, run the query, and return
        the result as a pydantic Output class. This is what will be returned as
        JSON via the FastAPI endpount. Fee free to do this however you'd like, but
        a its worth noting that the llama-index package has a CitationQueryEngine...

        Also, be sure to make use of self.k (the number of vectors to return based
        on semantic similarity).

        # Example output object
        citations = [
            Citation(source="Law 1", text="Theft is punishable by hanging"),
            Citation(source="Law 2", text="Tax evasion is punishable by banishment."),
        ]

        output = Output(
            query=query_str,
            response=response_text,
            citations=citations
            )

        return output

        """


if __name__ == "__main__":
    doc_serivce = DocumentService(
        filepath="docs/laws.pdf",
        parse_start=PDFPosition(page_number=0, y_coord=80),
        parse_end=PDFPosition(page_number=1, y_coord=640),
    )
    docs = doc_serivce.create_documents()

    index = QdrantService()
    index.connect()
    index.load(docs)

    index.query("what happens if I steal?")  # NOT implemented
