"""
Module to load the data into BigQuery. It takes the dictionary output from the Graph and load it into a BigQuery Table
using a predefined schema.
it includes:
1. The SCHEMA: design to be a static variable (Caps for that reason), takes the entries from the Graph and conform them
to the schema expected by BigQuery Table.
2.load_data_to_bigquery: THe function connected with the Google client and uploads the data into BIgQuery Tables.
"""

from typing import Dict

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

# Define schema
SCHEMA = [
    bigquery.SchemaField("document_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("publication_date", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("authors", "STRING", mode="REPEATED"),
    bigquery.SchemaField("key_words", "STRING", mode="REPEATED"),
    bigquery.SchemaField("key_points", "STRING", mode="REPEATED"),
    bigquery.SchemaField("summary", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("methodology", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("processed_timestamp", "STRING", mode="REQUIRED"),
]


def load_data_to_bigquery(
    project_id: str, dataset_id: str, table_id: str, data: Dict
) -> None:
    """Loads data into a specified BigQuery table.

    This function connects to Google BigQuery and loads the provided data into
    the specified table. If the table does not exist, it will be created with
    a predefined schema. The function also handles errors that may occur during
    the insertion of data.
    Args:
        project_id (str): The Google Cloud project ID where the BigQuery dataset resides.
        dataset_id (str): The ID of the BigQuery dataset where the table is located.
        table_id (str): The ID of the BigQuery table where the data will be inserted.
        data (Dict): A dictionary containing the data to insert into the table.
                     It is expected to have a key "extracted_info" that holds
                     a list of dictionaries representing the rows to be inserted.
    Returns:
        None: This function does not return a value. It prints messages indicating
        the success or failure of the data insertion process.
    Raises:
        google.cloud.exceptions.NotFound: If the specified dataset or table does not exist
        and cannot be created.
    """
    client = bigquery.Client(project=project_id)

    # Create dataset reference
    dataset_ref = bigquery.DatasetReference(dataset_id)

    # Create table reference
    table_ref = dataset_ref.table(table_id)

    # Check if table exists, if not create it
    try:
        table = client.get_table(table_ref)
    except NotFound:
        table = bigquery.Table(table_ref, schema=SCHEMA)
        table = client.create_table(table)
        print(f"Table {table_id} created in dataset {dataset_id}.")

    # Insert rows
    errors = client.insert_rows_json(table, data["extracted_info"])
    if errors:
        print(f"Errors occurred while inserting rows: {errors}")
    else:
        print(f"Data successfully inserted into {table_id}.")
