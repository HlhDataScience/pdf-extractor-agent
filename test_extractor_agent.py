"""File module to test all the functions for our app"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock

from langchain_core.documents.base import Document

from src.PdfExtractor import pdf_extractor
from src.PydanticSchema import (  # Update this import path as needed
    BigQueryEntry,
    validate_list_length,
    validate_non_empty_string,
    validate_string_length,
)


class TestPDFExtractorAgent(unittest.TestCase):
    """This is a class updatable for every single function in order to test them with the commit stage."""

    def setUp(self):
        """Set up test data that will be used across multiple tests"""
        self.valid_doc_data = {
            "document_id": "doc_2024_001",
            "title": "Example Document",
            "date": "2024-01-21",
            "authors": ["John Doe", "Jane Smith"],
            "key_points": ["First main point", "Second main point"],
            "summary": "A brief summary of the document content",
        }

    def test_pdf_extractor(self, mock_loader):
        """This function tests the pdf_extractor function of the app"""
        # Arrange
        mock_path = "sample.pdf"
        mock_content = "This is a test document."

        # Create a mock loader instance
        mock_loader_instance = MagicMock()
        mock_loader.return_value = mock_loader_instance

        # Mock the loader's load method
        mock_doc = Document(page_content=mock_content)
        mock_loader_instance.load.return_value = [mock_doc]

        # Act
        result = pdf_extractor(path_pdf=mock_path)

        # Assert
        self.assertIsInstance(result, list, "Result should be a list.")
        self.assertGreater(len(result), 0, "Result list should not be empty.")
        self.assertIsInstance(
            result[0], Document, "Result should contain Document objects."
        )
        self.assertEqual(
            result[0].page_content,
            mock_content,
            "Document content should match expected content.",
        )

    def test_validate_non_empty_string(self):
        """Test the non-empty string validator"""
        self.assertEqual(validate_non_empty_string("test"), "test")
        self.assertEqual(validate_non_empty_string("  test  "), "test")

        with self.assertRaises(ValueError) as context:
            validate_non_empty_string("")
        self.assertTrue("String must not be empty" in str(context.exception))

        with self.assertRaises(ValueError) as context:
            validate_non_empty_string("   ")
        self.assertTrue("String must not be empty" in str(context.exception))

    def test_validate_string_length(self):
        """Test the string length validator"""
        validator = validate_string_length(5)
        self.assertEqual(validator("test"), "test")

        with self.assertRaises(ValueError) as context:
            validator("too long")
        self.assertTrue("String must not exceed 5 characters" in str(context.exception))

    def test_validate_list_length(self):
        """Test the list length validator"""
        validator = validate_list_length(2)
        self.assertEqual(validator(["one", "two"]), ["one", "two"])

        with self.assertRaises(ValueError) as context:
            validator(["one", "two", "three"])
        self.assertTrue("List must not exceed 2 items" in str(context.exception))

    def test_valid_document_creation(self):
        """Test creation of a valid BigQueryEntry instance"""
        doc = BigQueryEntry(**self.valid_doc_data)
        self.assertEqual(doc.document_id, self.valid_doc_data["document_id"])
        self.assertEqual(doc.title, self.valid_doc_data["title"])
        self.assertEqual(doc.date, self.valid_doc_data["date"])
        self.assertEqual(doc.authors, self.valid_doc_data["authors"])
        self.assertEqual(doc.key_points, self.valid_doc_data["key_points"])
        self.assertEqual(doc.summary, self.valid_doc_data["summary"])

        # Verify processed_timestamp is in ISO format
        try:
            datetime.fromisoformat(doc.processed_timestamp)
        except ValueError:
            self.fail("processed_timestamp is not in valid ISO format")

    def test_invalid_document_id(self):
        """Test document_id validation"""
        invalid_data = self.valid_doc_data.copy()
        invalid_data["document_id"] = "invalid@id"

        with self.assertRaises(ValueError) as context:
            BigQueryEntry(**invalid_data)
        self.assertTrue(
            "document_id must contain only letters" in str(context.exception)
        )

    def test_invalid_date_format(self):
        """Test date format validation"""
        invalid_data = self.valid_doc_data.copy()
        invalid_data["date"] = "2024/01/21"

        with self.assertRaises(ValueError) as context:
            BigQueryEntry(**invalid_data)
        self.assertTrue("Date must be in YYYY-MM-DD format" in str(context.exception))

    def test_field_length_limits(self):
        """Test length limits for various fields"""
        # Test title length (1024 chars)
        doc_data = self.valid_doc_data.copy()
        doc_data["title"] = "x" * 1024
        try:
            BigQueryEntry(**doc_data)
        except ValueError:
            self.fail("Title with exactly 1024 characters should be valid")

        doc_data["title"] = "x" * 1025
        with self.assertRaises(ValueError):
            BigQueryEntry(**doc_data)

        # Test author name length (256 chars)
        doc_data = self.valid_doc_data.copy()
        doc_data["authors"] = ["x" * 256]
        try:
            BigQueryEntry(**doc_data)
        except ValueError:
            self.fail("Author name with exactly 256 characters should be valid")

        doc_data["authors"] = ["x" * 257]
        with self.assertRaises(ValueError):
            BigQueryEntry(**doc_data)

    def test_list_size_limits(self):
        """Test size limits for lists"""
        # Test authors list limit
        doc_data = self.valid_doc_data.copy()
        doc_data["authors"] = ["Author"] * 100  # Should pass
        try:
            BigQueryEntry(**doc_data)
        except ValueError:
            self.fail("100 authors should be valid")

        doc_data["authors"] = ["Author"] * 101
        with self.assertRaises(ValueError) as context:
            BigQueryEntry(**doc_data)
        self.assertTrue("List must not exceed 100 items" in str(context.exception))

        # Test key_points list limit
        doc_data = self.valid_doc_data.copy()
        doc_data["key_points"] = ["Point"] * 50  # Should pass
        try:
            BigQueryEntry(**doc_data)
        except ValueError:
            self.fail("50 key points should be valid")

        doc_data["key_points"] = ["Point"] * 51
        with self.assertRaises(ValueError) as context:
            BigQueryEntry(**doc_data)
        self.assertTrue("List must not exceed 50 items" in str(context.exception))


if __name__ == "__main__":
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(TestPDFExtractorAgent)
    )
