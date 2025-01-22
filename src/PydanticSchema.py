"""
This module houses the pydantic model that will help to estructure text for llm extraction and BigQuery format.
This includes:
5. custom validation functions: THis functions ensures that, if we send the structured info to BigQuery, those entries will conform with the expected format estructure.
4. type definitions: Using annotated, we created specific variable types that will be helpful when checking the format of the information extracted by the LLM.
3. class BigQueryEntry: THis Pydantic BaseModel is the base to estructure the output of the LLM call. It contains all the necessary fields and the basic schema example for the llm call.
4. class PDFValidator: small utility class that only checks that the streamlit app is receiving the correct input.
"""

# LINE 193: #We need to come back here and changed to V2 VALIDATOR USE
import re
from datetime import datetime, timezone
from typing import Annotated, Callable, List

from pydantic import (  # ValidationInfo We need to use this one for the @field_validation functions.
    BaseModel,
    Field,
    field_validator,
)
from pydantic.functional_validators import (  # Dataclass that allow us to perform a second pass over the format in a pydantic class, after the class itself has validated the entry data. Useful with BigQuery formatting.
    AfterValidator,
)


def validate_non_empty_string(v: str) -> str:
    """Validates that the provided string is not empty.
    This function checks if the input string is non-empty after stripping
    whitespace. If the string is empty, a ValueError is raised.
    Args:
        v (str): The string to validate.
    Returns:
        str: The trimmed string if it is non-empty.
    Raises:
        ValueError: If the string is empty after stripping whitespace.
    """
    if not v.strip():
        raise ValueError("String must not be empty")
    return v.strip()


def validate_string_length(max_length: int) -> Callable[[str], str]:
    """Creates a validation function to check string length.
    This function returns a validation function that checks if a given string
    does not exceed the specified maximum length. If the string exceeds the
    maximum length, a ValueError is raised.
    Args:
        max_length (int): The maximum allowed length for the string.
    Returns:
        Callable[[str], str]: A validation function that checks the length of
        a string.
    """

    def validate(v: str) -> str:
        """Validates that the string does not exceed the maximum length.
        Args:
            v (str): The string to validate.
        Returns:
            str: The validated string if it does not exceed the maximum length.
        Raises:
            ValueError: If the string exceeds the maximum length.
        """
        if len(v) > max_length:
            raise ValueError(f"String must not exceed {max_length} characters")
        return v

    return validate


def validate_list_length(max_items: int) -> Callable[[List[str]], List[str]]:
    """Creates a validation function to check the length of a list.
    This function returns a validation function that checks if a given list
    does not exceed the specified maximum number of items. If the list exceeds
    the maximum number of items, a ValueError is raised.
    Args:
        max_items (int): The maximum allowed number of items in the list.
    Returns:
        Callable[[List[str]], List[str]]: A validation function that checks
        the length of a list of strings.
    """

    def validate(v: List[str]) -> List[str]:
        """Validates that the list does not exceed the maximum number of items.
        Args:
            v (List[str]): The list to validate.
        Returns:
            List[str]: The validated list if it does not exceed the maximum
            number of items.
        Raises:
            ValueError: If the list exceeds the maximum number of items.
        """
        if len(v) > max_items:
            raise ValueError(f"List must not exceed {max_items} items")
        return v

    return validate


# Type definitions using Annotated
NonEmptyString = Annotated[str, AfterValidator(validate_non_empty_string)]
ShortString = Annotated[NonEmptyString, AfterValidator(validate_string_length(256))]
LongString = Annotated[NonEmptyString, AfterValidator(validate_string_length(1024))]
VeryLongString = Annotated[NonEmptyString, AfterValidator(validate_string_length(4096))]


class BigQueryEntry(BaseModel):
    """Pydantic model representing a structured entry for BigQuery.

    This model defines the structure of information extracted from documents,
    including validation rules that conform to BigQuery requirements. Each field
    is annotated with validation constraints to ensure data integrity.

    Attributes:
        document_id (str): A unique identifier for the document, validated to
            match specific character requirements and length.
        title (LongString): The title of the document, validated to be a non-empty
            string with a maximum length of 1024 characters.
        publication_date (str): The date of publication in YYYY-MM-DD format,
            validated for correct formatting.
        authors (List[ShortString]): A list of authors of the document, validated
            to contain a maximum of 100 items, each being a non-empty string
            with a maximum length of 256 characters.
        key_words (List[ShortString]): A list of summary keywords for the document,
            validated to contain a maximum of 50 items, each being a non-empty
            string with a maximum length of 256 characters.
        key_points (List[LongString]): A list of main points or findings from the
            document, validated to contain a maximum of 50 items, each being a
            non-empty string with a maximum length of 1024 characters.
        summary (VeryLongString): A brief summary of the document, validated to
            be a non-empty string with a maximum length of 4096 characters.
        methodology (VeryLongString): A brief summary of the methodology used in
            the article, validated to be a non-empty string with a maximum length
            of 4096 characters.
        processed_timestamp (str): A timestamp indicating when the document was
            processed, automatically generated in ISO 8601 format.

    Validators:
        validate_date: Ensures the publication date is in the correct format.
        validate_document_id: Ensures the document ID contains only valid characters.
    """

    document_id: Annotated[
        str,
        Field(description="Unique identifier for the document"),
        AfterValidator(validate_string_length(1024)),
    ]

    title: LongString = Field(description="The title of the document")

    publication_date: Annotated[
        str,
        Field(
            description="The date of publication of the document in YYYY-MM-DD format"
        ),
    ]

    authors: Annotated[
        List[ShortString],
        Field(description="List of authors of the document"),
        AfterValidator(validate_list_length(100)),
    ]

    key_words: Annotated[
        List[ShortString],
        Field(description="The summary keywords of the document"),
        AfterValidator(validate_list_length(50)),
    ]

    key_points: Annotated[
        List[LongString],
        Field(description="Main points or findings from the document"),
        AfterValidator(validate_list_length(50)),
    ]

    summary: VeryLongString = Field(description="A brief summary of the document")

    methodology: VeryLongString = Field(
        description="A brief summary of the methodology used in the article."
    )

    processed_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @field_validator("publication_date")
    def validate_date(cls, v):
        """Validates that the publication date is in the correct format.
        Args:
            cls: The class itself.
            v (str): The publication date to validate.
        Returns:
            str: The validated publication date.
        Raises:
            ValueError: If the date is not in YYYY-MM-DD format.
        """
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    @field_validator("document_id")
    def validate_document_id(cls, v):  # We need to come back here and changed to V2
        """Validates that the document ID contains only valid characters.
        Args:
            cls: The class itself.
            v (str): The document ID to validate.
        Returns:
            str: The validated document ID.
        Raises:
            ValueError: If the document ID contains invalid characters.
        """
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "document_id must contain only letters, numbers, hyphens, and underscores"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "document_id": "doc_2024_001",
                    "title": "Example Document",
                    "publication_date": "2024-01-21",
                    "authors": ["John Doe", "Jane Smith"],
                    "key_words": ["key1", "key2"],
                    "key_points": ["First main point", "Second main point"],
                    "summary": "A brief summary of the document content",
                    "methodology": "A brief description of the methodology used",
                    "processed_timestamp": "2024-01-21T10:00:00.000Z",
                }
            ]
        }
    }


class PDFValidator(BaseModel):
    """Validation model for PDF file inputs in the application.

    This class defines a simple validation mechanism for ensuring that the
    provided file name corresponds to a PDF file. It includes a single field
    with validation rules.

    Attributes:
        file_name (str): The name of the file to validate, which must end with
            the '.pdf' extension.

    Validators:
        validate_pdf: Ensures that the file name ends with '.pdf'.
    """

    file_name: str

    @field_validator("file_name")
    def validate_pdf(cls, file_name: str) -> str:
        """Validates that the file name corresponds to a PDF file.

        Args:
            cls: The class itself.
            file_name (str): The name of the file to validate.

        Returns:
            str: The validated file name.

        Raises:
            ValueError: If the file name does not end with '.pdf'.
        """
        if not file_name.endswith(".pdf"):
            raise ValueError("File must be a PDF.")
        return file_name
