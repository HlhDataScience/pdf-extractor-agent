"""main program entry"""

import os
import tempfile

import streamlit as st
from pydantic import ValidationError

# from src.BigQueryLoader import load_data_to_bigquery
from src.GraphModel import workflow_run
from src.PydanticSchema import PDFValidator


# Streamlit app
def main():
    """Main entry for the streamlit app"""
    st.title("LangGraph PDF Processor")

    # Step 1: API Key Input and GC JSON credentials"
    api_key = st.text_input(
        "Enter your OpenAI API Key (Don´t worry, we delete your info after the process):",
        type="password",
    )
    if not api_key:
        st.warning("Please enter your API key.")
        st.stop()
    # google_credentials_path = st.file_uploader(
    #        "Enter the path to your Google Cloud credentials JSON file:",
    #    )
    #    if not google_credentials_path:
    #       st.warning("Please provide the path to your Google Cloud credentials.")
    #        st.stop()

    # Set Google Cloud credentials
    #    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path
    #    project_id = st.text_input("Enter the project id:", key="project_id")
    #    dataset_id = st.text_input("Enter the first parameter:", key="dataset_id")
    #    table_id = st.text_input("Enter the first parameter:", key="table_id")
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
