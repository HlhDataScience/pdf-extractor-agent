"""File module to test all the functions for our app"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.BigQueryLoader import load_data_to_bigquery
from src.LlmModel import extract_information, process_pdf
from src.PydanticSchema import BigQueryEntry


class TestLlmModelFunctions(unittest.TestCase):
    """Tests for the LLM model file functions."""

    def setUp(self):
        """Set up test data that will be used across multiple tests"""
        self.valid_state = {
            "pdf_text": "",
            "extracted_info": None,
            "error": None,
        }

        self.valid_doc_data = {
            "document_id": "doc_2024_001",
            "title": "Example Document",
            "publication_date": "2024-01-21",
            "authors": ["John Doe", "Jane Smith"],
            "key_words": ["key1", "key2"],
            "key_points": ["First main point", "Second main point"],
            "summary": "A brief summary of the document content",
            "methodology": "a brief description of tte methodology used",
            "processed_timestamp": "2024-01-21T10:00:00.000Z",
        }

    @patch("src.LlmModel.PyPDFLoader")
    def test_process_pdf_valid(self, mock_loader):
        """Test processing a valid PDF"""
        mock_path = "sample.pdf"
        mock_text = "This is a test document."

        # Mock the PyPDFLoader
        mock_loader_instance = MagicMock()
        mock_loader.return_value = mock_loader_instance
        mock_loader_instance.load.return_value = [MagicMock(page_content=mock_text)]

        # Act
        result_state = process_pdf(self.valid_state, mock_path)

        # Assert
        self.assertEqual(result_state["pdf_text"], mock_text)
        self.assertIsNone(result_state["error"], "Error should be None for valid PDF")

    @patch("src.LlmModel.PyPDFLoader")
    def test_process_pdf_invalid(self, mock_loader):
        """Test processing an invalid PDF"""
        mock_loader.side_effect = Exception("File not found")
        mock_path = "nonexistent.pdf"

        # Act
        result_state = process_pdf(self.valid_state, mock_path)

        # Assert
        self.assertIn("Error processing the pdf", result_state["error"])

    @patch("src.LlmModel.ChatOpenAI")
    @patch("src.LlmModel.JsonOutputParser")
    @patch("src.LlmModel.ChatPromptTemplate")
    def test_extract_information_valid(
        self, mock_prompt_template, mock_parser, mock_llm
    ):
        """Test extracting information from a valid state"""
        valid_text = "This is a valid document text."
        self.valid_state["pdf_text"] = valid_text

        # Mock LLM, Parser, and PromptTemplate
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        mock_llm_instance.invoke.return_value = self.valid_doc_data

        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.get_format_instructions.return_value = (
            "format instructions"
        )
        mock_parser_instance.parse.return_value = self.valid_doc_data

        mock_prompt_instance = MagicMock()
        mock_prompt_template.from_messages.return_value = mock_prompt_instance
        mock_prompt_instance.invoke.return_value = self.valid_doc_data

        # Act
        result_state = extract_information(self.valid_state)

        # Assert
        self.assertEqual(result_state["extracted_info"], self.valid_doc_data)
        self.assertIsNone(
            result_state["error"], "Error should be None for valid extraction"
        )

    @patch("src.LlmModel.ChatOpenAI")
    def test_extract_information_error(self, mock_llm):
        """Test extracting information when LLM raises an error"""
        valid_text = "This is a valid document text."
        self.valid_state["pdf_text"] = valid_text

        # Mock LLM to raise an exception
        mock_llm.side_effect = Exception("LLM Error")

        # Act
        result_state = extract_information(self.valid_state)

        # Assert
        self.assertIn("Error Extracting information", result_state["error"])

    # Additional validation and BigQueryEntry tests remain unchanged
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

    # Other validation tests can follow...


class TestBigQueryLoaderFunctions(unittest.TestCase):
    """Tests for the load_data_to_bigquery function."""

    def setUp(self):
        """Set up test data that will be used across multiple tests"""
        self.valid_data = {
            "extracted_info": [
                {
                    "document_id": "doc_2024_001",
                    "title": "Example Document",
                    "publication_date": "2024-01-21",
                    "authors": ["John Doe", "Jane Smith"],
                    "key_words": ["key1", "key2"],
                    "key_points": ["First main point", "Second main point"],
                    "summary": "A brief summary of the document content",
                    "methodology": "a brief description of the methodology used",
                    "processed_timestamp": "2024-01-21T10:00:00.000Z",
                }
            ]
        }

        self.project_id = "test-project"
        self.dataset_id = "test-dataset"
        self.table_id = "test-table"

    @patch("google.cloud.bigquery.Client")
    def test_load_data_to_bigquery_success(self, mock_client):
        """Test successful data insertion into BigQuery"""
        mock_bq_client = MagicMock()
        mock_client.return_value = mock_bq_client

        # Mock the table reference and insertion
        mock_table = MagicMock()
        mock_bq_client.get_table.return_value = mock_table
        mock_bq_client.insert_rows_json.return_value = []

        # Act
        load_data_to_bigquery(
            self.project_id, self.dataset_id, self.table_id, self.valid_data
        )

        # Assert
        mock_bq_client.insert_rows_json.assert_called_once_with(
            mock_table, self.valid_data["extracted_info"]
        )
        print("Test successful data insertion passed")

    @patch("google.cloud.bigquery.Client")
    def test_create_table_if_not_exists(self, mock_client):
        """Test that the table is created if it doesn't exist"""
        mock_bq_client = MagicMock()
        mock_client.return_value = mock_bq_client

        # Mock NotFound exception for table
        mock_bq_client.get_table.side_effect = NotFound("Table not found")

        # Mock the table creation
        mock_table = MagicMock()
        mock_bq_client.create_table.return_value = mock_table

        # Act
        load_data_to_bigquery(
            self.project_id, self.dataset_id, self.table_id, self.valid_data
        )

        # Assert
        mock_bq_client.create_table.assert_called_once()
        print("Test table creation passed")

    @patch("google.cloud.bigquery.Client")
    def test_insert_data_error(self, mock_client):
        """Test the error handling when insert_rows_json fails"""
        mock_bq_client = MagicMock()
        mock_client.return_value = mock_bq_client

        # Mock the table reference
        mock_table = MagicMock()
        mock_bq_client.get_table.return_value = mock_table

        # Mock the insert_rows_json to return an error
        mock_bq_client.insert_rows_json.return_value = [
            {"index": 0, "errors": "Error occurred"}
        ]

        # Act
        with self.assertLogs(level="INFO") as log:
            load_data_to_bigquery(
                self.project_id, self.dataset_id, self.table_id, self.valid_data
            )

        # Assert
        self.assertIn("Errors occurred while inserting rows:", log.output[0])
        print("Test data insertion error handling passed")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestBigQueryLoaderFunctions)
    )
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLlmModelFunctions))

    unittest.TextTestRunner().run(suite)
