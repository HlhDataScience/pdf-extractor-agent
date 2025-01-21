"""main program entry"""

import os
import tempfile

import streamlit as st
from pydantic import ValidationError

from src.GraphModel import workflow_run
from src.PydanticSchema import PDFValidator


# Streamlit app
def main():
    """Main entry for the streamlit app"""
    st.title("LangGraph PDF Processor")

    # Step 1: API Key Input
    api_key = st.text_input(
        "Enter your OpenAI API Key (Don´t worry, we delete your info after the process):",
        type="password",
    )
    if not api_key:
        st.warning("Please enter your API key.")
        st.stop()

    # Step 2: File Upload
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file is not None:
        try:
            # Validate the uploaded file
            PDFValidator(file_name=uploaded_file.name)

            temp_dir = tempfile.TemporaryDirectory()
            temp_path = os.path.join(temp_dir.name, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            os.environ["OPENAI_API_KEY"] = api_key

            st.info("Processing the PDF...")
            result = workflow_run(
                pdf_path=temp_path
            )  # LangGraph will use the environment variable
            st.info("PDF file processed.")
            st.info("removing your file and API Key information from our system")
            os.remove(temp_path)
            temp_dir.cleanup()
            # Cleanup: Delete the API key from the environment
            del os.environ["OPENAI_API_KEY"]
            st.success("Processing complete!")
            st.write("Result:", result)

        except ValidationError as e:
            st.error(f"Validation error: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
