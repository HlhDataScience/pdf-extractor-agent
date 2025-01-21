"""LLM model file"""

from typing import Optional, TypedDict

from langchain.document_loaders import PyPDFLoader
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.PydanticSchema import BigQueryEntry

# First is to define the state of the graph, which is going to take the actions performed into its object


class State(TypedDict):
    """Typed Dict that allow as to control the flow of the graph, as it represents the states for which the graph has to pass"""

    pdf_text: str
    extracted_info: Optional[BigQueryEntry]
    error: Optional[str]


# Redefined function to extract text from pdfs


def process_pdf(state: State, pdf_path: str) -> State:
    """This function takes a pdf path and return a State class to be further processed by a LLM."""
    try:
        loader = PyPDFLoader(file_path=pdf_path)
        docs = loader.load()
        text = "\n".join(page.page_content for page in docs)
        state["pdf_text"] = text
        return state
    except Exception as e:
        state["error"] = f"Error processing the pdf: {str(e)}"
        return state


def extract_information(state: State) -> State:
    """This function takes the State class raw text and transform it into BigQuery formaTED ENTRIES WITH the help of llms"""
    if "error" in state and state["error"]:
        return state
    try:
        llm = ChatAnthropic(
            model="claude-3-sonnet-20240229", temperature=0, max_tokens=4000
        )

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

        # running the chain

        result = chain.invoke(
            {
                "text": state["pdf_text"],
                "format_instructions": parser.get_format_instructions(),
            }
        )

        state["extracted_info"] = result
        return state

    except Exception as e:
        state["error"] = f"Error Extracting information: {str(e)}"
        return state
