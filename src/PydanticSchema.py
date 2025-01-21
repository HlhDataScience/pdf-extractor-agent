"""This module houses the pydantic model that will help to estructure text for llm extraction and BigQuery format."""

import re
from datetime import datetime, timezone
from typing import Annotated, List

from pydantic import BaseModel, Field, field_validator
from pydantic.functional_validators import AfterValidator


# Custom validation functions
def validate_non_empty_string(v: str) -> str:
    """Function that checks the string we send to BigQuery is not empty"""
    if not v.strip():
        raise ValueError("String must not be empty")
    return v.strip()


def validate_string_length(max_length: int):
    """Function that check we do not surpass the max_length limit for BigQuery format"""

    def validate(v: str) -> str:
        if len(v) > max_length:
            raise ValueError(f"String must not exceed {max_length} characters")
        return v

    return validate


def validate_list_length(max_items: int):
    """Function that check we do not surpass the max_length limit for BigQuery format"""

    def validate(v: List[str]) -> List[str]:
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
    """
    Pydantic model defining the structure of information to extract from documents,
    with validation rules matching BigQuery requirements.
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
    Key_words: Annotated[
        List[ShortString],
        Field(description="THe summary keywords of the document"),
        AfterValidator(validate_list_length(50)),
    ]

    key_points: Annotated[
        List[LongString],
        Field(description="Main points or findings from the document"),
        AfterValidator(validate_list_length(50)),
    ]

    summary: VeryLongString = Field(description="A brief summary of the document")

    methodology: VeryLongString = Field(
        description=" a brief summary of the methodology used in the article."
    )

    processed_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @field_validator("publication_date")
    def validate_date(cls, v):
        """Check the date is correctly introduced"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    @field_validator("document_id")
    def validate_document_id(cls, v):
        """Checks the unique identifiers"""
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
                    "date": "2024-01-21",
                    "authors": ["John Doe", "Jane Smith"],
                    "key_points": ["First main point", "Second main point"],
                    "summary": "A brief summary of the document content",
                    "processed_timestamp": "2024-01-21T10:00:00.000Z",
                }
            ]
        }
    }
