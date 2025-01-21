"""LLM model file"""

from typing import List, Optional, TypedDict

from langchain.document_loaders import PyPDFLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.PydanticSchema import BigQueryEntry

# First is to define the state of the graph, which is going to take the actions performed into its object


class State(TypedDict):
    """Typed Dict that allows us to control the flow of the graph, as it represents the states for which the graph has to pass"""

    pdf_text: str
    extracted_info: Optional[BigQueryEntry]
    error: Optional[str]


# Redefined function to extract text from PDFs
def split_text_into_chunks(text: str, max_tokens: int = 8000) -> List[str]:
    """
    Splits text into smaller chunks that fit within the token limit.
    """
    chunks = []
    words = text.split()
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def process_pdf(state: State, pdf_path: str) -> State:
    """This function takes a PDF path and returns a State class to be further processed by an LLM."""
    try:
        loader = PyPDFLoader(file_path=pdf_path)
        docs = loader.load()
        text = "\n".join(page.page_content for page in docs)
        state["pdf_text"] = text
        return state
    except Exception as e:
        state["error"] = f"Error processing the PDF: {str(e)}"
        return state


def extract_information(state: State) -> State:
    """This function takes the State class raw text and transforms it into BigQuery formatted entries with the help of LLMs."""
    if "error" in state and state["error"]:
        return state
    try:
        llm = ChatOpenAI(model="chatgpt-4o-latest", temperature=0)

        parser = JsonOutputParser(pydantic_object=BigQueryEntry)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert at extracting structured information from documents.
                    Extract the requested information from the text and format it according to the specified schema.
                    Be precise and factual in your extraction.""",
                ),
                (
                    "user",
                    "Extract the following information from this text: {text}\n\n{format_instructions}",
                ),
            ]
        )

        # Chain to be processed
        chain = prompt | llm | parser

        # Running the chain

        result = chain.invoke(
            {
                "text": state["pdf_text"],
                "format_instructions": parser.get_format_instructions(),
            }
        )

        state["extracted_info"] = result
        return state

    except Exception as e:
        state["error"] = f"Error extracting information: {str(e)}"
        return state
