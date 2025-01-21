"""Module to load the data into BIg Query"""

from typing import Dict

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

# Define schema statically
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


def load_data_to_bigquery(project_id: str, dataset_id: str, table_id: str, data: Dict):
    """
    Loads data into a BigQuery table.

    Args:
        project_id (str): Google Cloud project ID.
        dataset_id (str): BigQuery dataset ID.
        table_id (str): BigQuery table ID.
        data (list of dict): The data to insert into the table.

    Returns:
        None
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
