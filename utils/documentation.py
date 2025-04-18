import os
import json
from pathlib import Path
import graphviz
from utils.groq_llm import llama3_chat

def generate_workflow_graph(output_file="workflow_graph.png"):
    """
    Generating a visualization of the LangGraph workflow using Graphviz
    
    Args:
        output_file: Path to save the generated graph image
    
    Returns:
        Path to the generated file
    """
    # Create a new directed graph
    dot = graphviz.Digraph("LangGraph_Workflow", comment="SRS Analyzer Workflow")
    
    # Add nodes
    dot.node("extract_api", "Extract API Endpoints")
    dot.node("extract_logic", "Extract Business Logic")
    dot.node("extract_auth", "Extract Auth Requirements")
    dot.node("extract_db", "Extract DB Schema")
    dot.node("project_setup", "Project Setup")
    dot.node("generate_project", "Generate Project Structure")
    
    # Add edges
    dot.edge("extract_api", "extract_logic")
    dot.edge("extract_logic", "extract_auth")
    dot.edge("extract_auth", "extract_db")
    dot.edge("extract_db", "project_setup")
    dot.edge("project_setup", "generate_project")
    
    # Add subgraphs for phases
    with dot.subgraph(name="cluster_extraction") as s:
        s.attr(label="Data Extraction Phase")
        s.node_attr.update(style="filled", color="lightblue")
        s.node("extract_api")
        s.node("extract_logic")
        s.node("extract_auth")
        s.node("extract_db")
    
    with dot.subgraph(name="cluster_generation") as s:
        s.attr(label="Project Generation Phase")
        s.node_attr.update(style="filled", color="lightgreen")
        s.node("project_setup")
        s.node("generate_project")
    
    # Render the graph
    output_path = dot.render(filename='workflow', directory='docs', format='png', cleanup=True)
    
    return output_path

def generate_mermaid_diagram():
    """Generate a Mermaid diagram code for the workflow"""
    
    mermaid_code = """```mermaid
graph TD
    A[Extract API Endpoints] -->|api_endpoints| B[Extract Business Logic]
    B -->|api_endpoints, business_logic| C[Extract Auth Requirements]
    C -->|api_endpoints, business_logic, auth_requirements| D[Extract DB Schema]
    D -->|api_endpoints, business_logic, auth_requirements, db_schema| E[Project Setup]
    E -->|setup, api_endpoints, business_logic, auth_requirements, db_schema| F[Generate Project Structure]

    subgraph "Data Extraction Phase"
    A
    B
    C
    D
    end

    subgraph "Project Generation Phase"
    E
    F
    end
```"""
    
    # Save the mermaid diagram code to a file
    os.makedirs('docs', exist_ok=True)
    with open('docs/workflow_diagram.md', 'w') as f:
        f.write("# SRS Analyzer Workflow\n\n")
        f.write(mermaid_code)
    
    return 'docs/workflow_diagram.md'

def generate_project_documentation(state, output_dir="docs"):
    """
    Generate project documentation using LLM
    
    Args:
        state: The final state from the LangGraph workflow
        output_dir: Directory to store documentation
    
    Returns:
        Dict with paths to generated files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract data from state
    api_endpoints = state.get("api_endpoints", "{}")
    business_logic = state.get("business_logic", "{}")
    auth_requirements = state.get("auth_requirements", "{}")
    db_schema = state.get("db_schema", "{}")
    
    # Generate README.md
    readme_prompt = f"""
    Generate a comprehensive README.md file for an SRS Analyzer project that:
    1. Analyzes SRS documents to extract API endpoints, business logic, authentication requirements, and database schema
    2. Creates a full FastAPI project based on the analysis
    3. Sets up the database schema automatically
    
    Include the following sections:
    - Project title and description
    - Features
    - Setup instructions (prerequisites, installation, configuration)
    - Usage instructions
    - Project structure
    - Generated project structure
    
    Here's the data extracted from the SRS to help you understand the project:
    API Endpoints: {api_endpoints}
    Business Logic: {business_logic}
    Auth Requirements: {auth_requirements}
    DB Schema: {db_schema}
    
    Use proper Markdown formatting. Keep it professional but friendly.
    """
    
    readme_content = llama3_chat(readme_prompt)
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write(readme_content)
    
    # Generate API Documentation
    api_doc_prompt = f"""
    Generate detailed API documentation for a FastAPI project in Markdown format.
    
    The documentation should include:
    1. Introduction to the SRS Analyzer API
    2. Endpoint documentation for the SRS analysis endpoint
    3. Documentation for the endpoints that would be generated in the resulting project
    
    Include these endpoints from the analyzed SRS:
    {api_endpoints}
    
    For each endpoint include:
    - HTTP method and path
    - Description
    - Request parameters/body
    - Response format
    - Example usage
    
    Also include a section on authentication based on:
    {auth_requirements}
    
    Format the documentation with proper Markdown, including code blocks for examples.
    """
    
    api_doc_content = llama3_chat(api_doc_prompt)
    api_doc_path = os.path.join(output_dir, "API_DOCUMENTATION.md")
    with open(api_doc_path, "w") as f:
        f.write(api_doc_content)
    
    return {
        "readme": readme_path,
        "api_doc": api_doc_path,
        "workflow_diagram": generate_mermaid_diagram(),
        "workflow_graph": generate_workflow_graph()
    }