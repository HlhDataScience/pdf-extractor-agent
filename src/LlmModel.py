"""
LLM model file

In this module, we defined the LLM system.
This module includes:
1. class State: a TypedDict which allow us to control the workflow with an estructure.
2. Function process_pdf: a function that takes as input tje State and a pdf path and returns the update State with the clean raw text.
3. Function extract_information: THe function takes the updated State class from process_pdf. It creates the chain call
 to the llm and returns the updated State with the llm powered information extraction.
"""

# Imports
from typing import Dict, Optional, TypedDict

from langchain.document_loaders import PyPDFLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.PydanticSchema import BigQueryEntry


# First is to define the state of the graph, which is going to take the actions performed into its object
class State(TypedDict):
    """Represents the state of a graph traversal.

    This TypedDict is used to manage the flow of the graph by storing relevant
    information about the current state, including the text extracted from a PDF,
    any information extracted for BigQueryEntry pydantic format, and any errors encountered during
    processing.

    Attributes:
        pdf_text (str): The text extracted from the PDF document.
        extracted_info (Optional[BigQueryEntry]): Information extracted for BigQueryEntry pydantic model format,
            or None if no information has been extracted.
        error (Optional[str]): An error message if an error occurred during processing,
            or None if no errors were encountered.
    """

    pdf_text: str
    extracted_info: Optional[BigQueryEntry]
    error: Optional[str]


def process_pdf(state: State, pdf_path: str) -> State:
    """Processes a PDF file and updates the state with the extracted text.

    This function takes a `State` dictionary and a file path to a PDF document,
    loads the PDF, extracts its text, and updates the state with the extracted
    text. If an error occurs during processing, the state is updated with an
    error message.

    Args:
        state (State): A dictionary representing the current state of the graph,
            which will be updated with the extracted PDF text or an error message.
        pdf_path (str): The file path to the PDF document to be processed.

    Returns:
        State: The updated state dictionary containing the extracted PDF text or
            an error message if an error occurred during processing.
    """
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
    """Extracts structured information from the PDF text in the state.

    This function takes a configuration dictionary that contains the current state
    and attempts to extract structured information from the PDF text stored in the
    state. If an error is present in the state, it returns the state without making
    any changes. If the extraction is successful, the state is updated with the
    extracted information The information is structured using pydantic model schema.

    Args:
        config (Dict): A configuration dictionary that must contain a "state" key,
            which holds the current state of the graph.

    Returns:
        State: The updated state dictionary containing the extracted information
            or an error message if an error occurred during the extraction process.
    """
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
