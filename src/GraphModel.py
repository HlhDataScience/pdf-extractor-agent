"""
Graph agent system to process the pdf into raw text, maintaining the estructure and
extracts information in a json format with LLM.
it includes:
1. create_extraction_pdf: THis functions takes no input and returns the complete workflow of the Graph
2. workflow_run: THis function executes the Graph, compiling it and taking the State to be passed by the workflow and
returns a Dictionary with the results and errors, if any.
"""

from typing import Dict

from langgraph.graph import Graph

from src.LlmModel import State, extract_information, process_pdf


def create_extraction_pdf_graph() -> Graph:
    """Creates a graph workflow for PDF extraction and information processing.

    This function initializes a directed graph that defines the workflow for
    processing a PDF file and extracting information from it. The graph consists
    of two nodes: one for processing the PDF and another for extracting information.
    The nodes are connected to form a workflow, with defined entry and exit points.

    Returns:
        Graph: The constructed graph representing the PDF extraction workflow.
    """

    # Created the graph
    workflow = Graph()

    def process_pdf_node(input: Dict) -> Dict:
        """Wrapper function for processing PDF files in the graph.
        This function handles the invocation of the `process_pdf` function and
        formats the input and output for the graph.
        Args:
            input (Dict): A dictionary containing the current state and the PDF path.
        Returns:
            Dict: A dictionary containing the updated state after processing the PDF.
        """
        state = input["state"]
        pdf_path = input["pdf_path"]
        return {"state": process_pdf(state=state, pdf_path=pdf_path)}

    def extract_information_node(input: Dict) -> Dict:
        """Wrapper function for extracting information from the state.
        This function handles the invocation of the `extract_information` function
        and formats the input and output for the graph.
        Args:
            input (Dict): A dictionary containing the current state.
        Returns:
            Dict: A dictionary containing the updated state after extracting information.
        """
        return {"state": extract_information(input)}

    # Adding nodes to the graph
    workflow.add_node("process_pdf", process_pdf_node)
    workflow.add_node("extract_information", extract_information_node)

    # Adding edges
    workflow.add_edge(start_key="process_pdf", end_key="extract_information")

    # Setting entry and exit points for the graph
    workflow.set_entry_point("process_pdf")
    workflow.set_finish_point("extract_information")

    return workflow


def workflow_run(pdf_path: str) -> Dict:
    """Executes the PDF extraction workflow and returns the results.
    This function creates the graph workflow for processing a PDF file, compiles
    the graph, and executes it with the provided PDF path. It initializes the
    state and returns the results of the extraction process.
    Args:
        pdf_path (str): The file path to the PDF document to be processed.
    Returns:
        Dict: A dictionary containing the status of the operation and either the
            extracted information or an error message if an error occurred.
    """

    # Creates the graph
    workflow = create_extraction_pdf_graph()

    # Compiles it
    compiled_graph = workflow.compile(
        debug=True
    )  # used to check the process in the notebook. It is also useful with docker and streamlit

    # Initialization of the State class
    initial_state = State(pdf_text="", extracted_info=None, error=None)
    config = {"state": initial_state, "pdf_path": pdf_path}

    # Executing the graph Pipeline
    result = compiled_graph.invoke(input=config)
    result = result["state"]

    # Returning possible results.
    if result["error"]:
        return {"status": "error", "error": result["error"]}

    return {"status": "success", "extracted_info": result["extracted_info"]}
