"""Graph agent system"""

from typing import Dict

from langgraph.graph import Graph

from src.LlmModel import State, extract_information, process_pdf


def create_extraction_pdf_graph() -> Graph:
    """Creates the graph workflow to be used."""

    # Created the graph
    workflow = Graph()

    def process_pdf_node(input: Dict) -> Dict:
        """wrapper function that handles the function process_pdf for graph formatting"""
        state = input["state"]
        pdf_path = input["pdf_path"]
        return {"state": process_pdf(state=state, pdf_path=pdf_path)}

    def extract_information_node(input: Dict) -> Dict:
        """wrapper function that handles the function extract_information for graph formatting"""
        return {"state": extract_information(input)}

    # adding nodes to the graph
    workflow.add_node("process_pdf", process_pdf_node)
    workflow.add_node("extract_information", extract_information_node)

    # adding edges
    workflow.add_edge(start_key="process_pdf", end_key="extract_information")

    # Setting entry and exit points for the graph
    workflow.set_entry_point("process_pdf")
    workflow.set_finish_point("extract_information")

    return workflow


def workflow_run(pdf_path: str) -> Dict:
    """THis function executes the graph workflow and return a Dict to check the results."""

    # Creates the graph
    workflow = create_extraction_pdf_graph()

    # Compiles it
    compiled_graph = workflow.compile(
        debug=True
    )  # used to check the process in the notebook.

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
