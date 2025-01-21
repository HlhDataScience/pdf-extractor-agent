"""LLM model file"""

from typing import Dict, Optional, TypedDict

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


def process_pdf(state: State, pdf_path: str) -> State:
    """This function takes a config dict containing state and pdf_path and returns a State class."""
    try:
        loader = PyPDFLoader(file_path=pdf_path)
        docs = loader.load()
        text = "\n".join(page.page_content for page in docs)
        state["pdf_text"] = text
        return state
    except Exception as e:
        state["error"] = f"Error processing the PDF: {str(e)}"
        return state


def extract_information(config: Dict) -> State:
    """This function takes the config dict containing state and returns an updated state."""
    state = config["state"]
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
