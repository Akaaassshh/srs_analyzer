from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from utils.preprocess import read_docx
from graph_builder import build_langgraph
from utils.db import create_tables_from_schema
from utils.project_generator import generate_project_structure, setup_virtual_env
from utils.documentation import generate_project_documentation
import tempfile
import shutil
import json
import os



app = FastAPI(
    title="SRS Analyzer",
    description="Upload an SRS document and get the extracted API endpoints, authentication methods, and database schema.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-srs")

async def analyze_srs(file: UploadFile = File(...)):
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Read SRS text from .docx
    srs_text = read_docx(tmp_path)
    # Step 1: Initialize graph
    graph = build_langgraph()
    # Step 2: Run the LangGraph
    final_state = graph.invoke({"srs_text": srs_text})
    print("===========================================================")
    print(final_state["setup"])
     # Step 3: Parse db_schema
    try:
        db_schema_dict = json.loads(final_state["db_schema"])
        
        print("===========================================================")
        print(final_state["setup"])
        # Step 4: Create tables in PostgreSQL
        create_tables_from_schema(db_schema_dict)
        
        # Step 5: Generate project structure
        project_dir = os.path.join(os.getcwd(), "generated_project")
        print("===========================================================")
        print(final_state["setup"])
        success, message = generate_project_structure(final_state["setup"], project_dir)
        
        # Step 6: Set up virtual environment
        if success:
            env_success, env_message = setup_virtual_env(project_dir)
        else:
            env_success = False
            env_message = "Skipped due to project generation failure"

         # Step 7: Generate documentation
        doc_files = generate_project_documentation(final_state)
            
        return {
            "status": "success",
            "api_endpoints": json.loads(final_state["api_endpoints"]),
            "business_logic": final_state["business_logic"],
            "auth_requirements": final_state["auth_requirements"],
            "db_schema": db_schema_dict,
            "project_generation": {
                "success": success,
                "message": message,
                "virtual_env": {
                    "success": env_success,
                    "message": env_message
                }
            },
             "documentation": {
                "readme": f"/docs/static/{os.path.basename(doc_files['readme'])}",
                "api_documentation": f"/docs/static/{os.path.basename(doc_files['api_doc'])}",
                "workflow_diagram": f"/docs/static/{os.path.basename(doc_files['workflow_diagram'])}",
                "workflow_graph": f"/docs/static/{os.path.basename(doc_files['workflow_graph'])}"
            }
        }
    except json.JSONDecodeError as e:
        return {
            "status": "error", 
            "message": f"Failed to parse JSON: {str(e)}",
            "raw_db_schema": final_state["db_schema"]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to process: {str(e)}",
            "db_schema": final_state.get("db_schema", "Not available")
        }