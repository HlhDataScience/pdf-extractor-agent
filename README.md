# pdf-extractor-agent

#### An approach to Information Extraction from pdfs using `LangGraph`, `Streamlit` and `OpenAI` and `Google Cloud Platform`.

## Table of Contents

#### - [Introduction](#introduction)
#### - [Installation and Usage](#installation-and-usage)
  - [Local installation](#local-installation)
  - [Local Usage](#local-usage)
  - [Upload and Deploy in Google Cloud](#upload-and-deploy-in-google-cloud)
#### - [Testing](#testing)
#### - [Known Limitations](#known-limitations)
#### - [Author](#author)


## Introduction
pdf-extractor agent is an approach on how we can leverage LLM engines like `OpenAI` and generative IA app development
frameworks to create Information Retrieval Systems. In this case we focused on pdf extraction of research documents.
**Our app extract meaningful insights from the pdf documents and format then into a json friendly format for display to
the user**. **It preserves the raw text extracted with its original estructure**. Finally, **it uploads the data extracted 
to a `BigQuery` table**, once the json google credentials are given.The table is created, if it is not already present.
Therefore, **the app is completely compatible either you use it locally, deployed on `Streamlit` or pushed as a `Docker Image` to 
`Google Run`.**

Everything is managed with `uv` as it is a fast installing system and follow the PEP rules related to pyproject.toml.

**All the code has been commented in a comprehensive way**.
#### **Do you want to try the app? [click here](https://pdf-extractor-agent-ubvrzwaywspux5qldtkxla.streamlit.app/)**
## Installation and Usage
### Local installation
For convenience, we facilitate a `makefile` to install everything faster. Nevertheless, here you have the instructions
depending on your use. The first thing will be git cloning the repository.To clone it, open your terminal and run the
following command:

```bash
git clone https://github.com/HlhDataScience/pdf-extractor-agent
```
After that, you can use `make` to install all the program. If you want to install everything directly

```bash
make
```
This will install `pipx` in an isolated environment, install `uv` with `pipx install uv` and install the dependencies into a 
`.venv` directory. Alternatively, if you already has `pipx` you can use the other options from the `makefile`:
```bash
make install-uv #installs the uv with pipx
make install-deps # installs the dependencies for the project
```
### Local usage
Once you have everything install , you have 2 options to deploy the app: Locally and within the Streamlit space.

To deploy it locally, you just have to open your terminal with your virtual environment active and:

```bash
streamlit run main.py
```

This will deploy the app within your localhost. It will prompt for OpenAI API key. once given, add as many pdfs as you like, the graph model will process them and return the structure output within this fashion:
```python
{
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
```
#### **Important**: This model does not use explicitly the upload to `BigQuery`. To use that functionality, uncomment the code from  main.py:
```python
    # Collect the Google Cloud credentials and other inputs
    #google_credentials_json = st.text_area("Enter your Google Cloud credentials JSON:", height=300)
    #if st.button("Submit Google Credentials JSON file"):
        #if not google_credentials_json:
            #st.warning("Please provide the Google Cloud credentials JSON.")
            #st.stop()

    #try:
        # Parse the JSON input
        #credentials = json.loads(google_credentials_json)

        # Set environment variables based on parsed credentials
        #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials.get("client_email", "")

        # Extracting project, dataset, and table IDs from the credentials JSON
        #project_id = credentials.get("project_id", "")
        #dataset_id = credentials.get("dataset_id", "")
        #table_id = credentials.get("table_id", "")

        #if not project_id or not dataset_id or not table_id:
            #st.warning("Please ensure that project_id, dataset_id, and table_id are provided in the JSON.")
            #st.stop()

        # Display the extracted information
        #st.write(f"Project ID: {project_id}")
        #st.write(f"Dataset ID: {dataset_id}")
        #st.write(f"Table ID: {table_id}")

```
#### and
```python
# for result_name,  result in results:
#    load_data_to_bigquery(project_id=project_id, dataset_id=dataset_id, table_id= table_id, data= result["extracted_info"])
#    st.info(f"{result_name} successfully uploaded")
#    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
#    st.info("Data loaded to BigQuery")
# st.success("Data successfully loaded.")
```
uncommenting this code will result in the use of the function `load_data_to_bigquery`. The app will prompt for your `Google Cloud json credentials`.
Once the app has finished processing the pdf research papers, it will upload them one by one, creating a `BigQuery` table.
Once the app has done the process, the User API key is deleted from the app in order to preserve privacy. The json credentials as well.
### Upload and Deploy in Google Cloud
To deploy into `Google Cloud Platform` we need first to Dockerize our application. For convenience, we created a ready
to go `Dockerfile` to deploy, following the good practices to cache and reduce the size of the image
as much as possible.

First you need to install [Docker](https://docs.docker.com/get-started/get-docker/)
Just simply clone the repository and then, with your Google Cloud project ready, run the following command:

```bash
docker build -t eu.gcr.io/gcp_project_name/app_name:v1 .
```
You have to substitute `gcp_project_name/` and `app_name:v1` for your project and own name. We are just building the
image with a nomenclature that facilitates the transition to `Google Run`.

After the image is build, we need to do the following:
1. Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
2. initialize the gcloud and follow the steps:
````bash
gcloud init
````
3. Push the image to the container register of GCP:
```bash
docker push eu.gcr.io/gcp_project_name/app_name:v1
```
4. Go to you GCP project and look for Cloud run section. CLick on "Create service", choose your region and define the name of the service. After that, select your docker image and provide and update the port.
5. You can go to the app and use it as indicated in [Local Usage](#local-usage).

## Testing
We tested the modules with unitest system and, for those which unitest was not ideal, they were tested within the 
`jupyter notebook` called `pdf_extractor_graph.ipynb`.
A list of tested modules:
- `BigQueryLoader.py` : Tested its functionally as part of the pre-commit with `test_extractor_agent.py`
- `GraphModel.py`: Tested with the `pdf_extractor_graph.ipynb`
- `LlmModel.py`: Tested both with `test_extractor_agent.py` and `pdf_extractor_graph.ipynb`
- `PydanticSchema.py`: Tested its functionally as part of the pre-commit with `test_extractor_agent.py`

**The model was tested against 20 research papers as well as other pdfs, and it performs in an accurate fashion.**
## Known Limitations
After careful review, the app have the following limitations:
- The model chosen ("chatgpt-4o-latest") is **the one with the longest token context window**. But the **price is not adecuate**. **We could explore using another open source model, if computational power is available by servers or GCP.**
- It would be necessary to use the pydantic model developed to check the registers sent to the BigQuery table by validation and AfterValidators. It would be a simple correction.
- The Graph could benefit from using a [semantic router](https://github.com/aurelio-labs/semantic-router), which involves **expanding the functionality with chatbot infrastructure and tools**.
- The model was **only tested using "chatgpt-4o-latest" and with English pdf documents** Therefore, performance may vary depending on the language of the pdf.
- To really **check the performance** of the model, we should use tools like [scalene](https://github.com/plasma-umass/scalene), which allows a **non-intrusive reading of the use of memory and performance of the code for later production states**.
- Finally, we could use also [specialist](https://github.com/brandtbucher/specialist) to **check the bytecode** and improve the process of documents **checking which part of the python Bytecode has been specialized by the interpreter and which could benefit from it**.
## Author
[Héctor López Hidalgo](https://www.linkedin.com/in/hlh-generative-ai)

