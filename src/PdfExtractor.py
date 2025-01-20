"""pdf estructure extractor module"""

from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents.base import Document


def pdf_extractor(path_pdf: str) -> List[Document]:
    """This function takes a pdf path and return a list of Documents to be further processed by a LLM."""
    loader = PyPDFLoader(file_path=path_pdf)
    docs = loader.load()
    return docs
