"""main program entry"""

import os
import tempfile

import streamlit as st
from pydantic import ValidationError

from src import PDFValidator, workflow_run  # , load_data_to_bigquery


# Streamlit app
def main():
    """Main entry point for the Streamlit PDF processing application.

    This function initializes the Streamlit app, allowing users to upload PDF files
    for processing. It handles user input for the OpenAI API key, validates uploaded
    files, and processes each PDF using the LangGraph workflow. The results are displayed
    to the user, and any temporary files are cleaned up after processing.
    Steps:
        1. User inputs their OpenAI API key.
        2. User uploads one or more PDF files.
        3. Each uploaded PDF is validated and processed.
        4. Results are displayed, and temporary files are deleted.
    Raises:
        ValidationError: If the uploaded PDF file does not meet validation criteria.
        Exception: If any other error occurs during processing.
    Returns:
        None: This function does not return a value. It interacts with the Streamlit
        interface to display information and results to the user.
    """
    st.title("LangGraph PDF Processor")

    # Step 1: API Key Input and GC JSON credentials
    api_key = st.text_input(
        "Enter your OpenAI API Key (Don´t worry, we delete your info after the process):",
        type="password",
    )
    if st.button(
        "Submit API Key"
    ):  # changed the logic to wait for the button widget, as the warning was displaying before the user had a chance to introduce the API Key.
        if not api_key:
            st.warning("Please enter your API key.")
            st.stop()
        else:
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("API Key accepted!")

    # Collect the Google Cloud credentials and other inputs
    # google_credentials_json = st.text_area("Enter your Google Cloud credentials JSON:", height=300)
    # if st.button("Submit Google Credentials JSON file"):
    # if not google_credentials_json:
    # st.warning("Please provide the Google Cloud credentials JSON.")
    # st.stop()

    # try:
    # Parse the JSON input
    # credentials = json.loads(google_credentials_json)

    # Set environment variables based on parsed credentials
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials.get("client_email", "")

    # Extracting project, dataset, and table IDs from the credentials JSON
    # project_id = credentials.get("project_id", "")
    # dataset_id = credentials.get("dataset_id", "")
    # table_id = credentials.get("table_id", "")

    # if not project_id or not dataset_id or not table_id:
    # st.warning("Please ensure that project_id, dataset_id, and table_id are provided in the JSON.")
    # st.stop()

    # Display the extracted information
    # st.write(f"Project ID: {project_id}")
    # st.write(f"Dataset ID: {dataset_id}")
    # st.write(f"Table ID: {table_id}")

    # Step 2: File Upload (Multiple PDFs)

    uploaded_files = st.file_uploader(
        "Upload PDF files", type=["pdf"], accept_multiple_files=True
    )
    if uploaded_files:
        os.environ["OPENAI_API_KEY"] = api_key
        results = []

        try:
            for uploaded_file in uploaded_files:
                # Validate the uploaded file
                PDFValidator(file_name=uploaded_file.name)

                # Save uploaded file temporarily
                temp_dir = tempfile.TemporaryDirectory()
                temp_path = os.path.join(temp_dir.name, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Process with LangGraph
                st.info(f"Processing {uploaded_file.name}...")
                result = workflow_run(
                    pdf_path=temp_path
                )  # LangGraph will use the environment variable
                results.append((uploaded_file.name, result))

                # Cleanup: Delete the temporary file
                os.remove(temp_path)
                temp_dir.cleanup()

            # Cleanup: Delete the API key from the environment
            del os.environ["OPENAI_API_KEY"]

            # Display Results
            st.info("Deleting your files and API key from our system.")
            st.success("Processing complete!")
            for file_name, result in results:
                st.write(f"**{file_name}:**", result)

                # for result_name,  result in results:

                #    load_data_to_bigquery(project_id=project_id, dataset_id=dataset_id, table_id= table_id, data= result["extracted_info"])
                #    st.info(f"{result_name} successfully uploaded")
                #    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
                #    st.info("Data loaded to BigQuery")
                # st.success("Data successfully loaded.")

        except ValidationError as e:
            st.error(f"Validation error: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
