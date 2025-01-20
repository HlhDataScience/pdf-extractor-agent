"""File module to test all the functions for our app"""

import unittest
from unittest.mock import MagicMock, patch

from langchain_core.documents.base import Document

from src.PdfExtractor import pdf_extractor


class TestPDFExtractor(unittest.TestCase):
    """This is a class updatable for every single function in order to test them with the commit stage."""

    @patch("PdfExtractor.PyPDFLoader")  # Adjust the import path as necessary
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


if __name__ == "__main__":
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(TestPDFExtractor)
    )
