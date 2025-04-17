from langgraph.graph import StateGraph
from nodes.extract_api import extract_api_node
from nodes.extract_logic import extract_logic_node
from nodes.extract_auth import extract_auth_node
from nodes.extract_db_data import extract_db_data_node
from nodes.project_setup import setup_node

from typing import TypedDict, Optional

# Define your state properly using TypedDict
class MyStateGraph(TypedDict):
    srs_text: str
    api_endpoints: Optional[str]
    auth_requirements: Optional[str]
    db_schema: Optional[str]
    business_logic: Optional[str]
    setup: Optional[str]

def build_langgraph():
    builder = StateGraph(MyStateGraph)
    builder.add_node("extract_api", extract_api_node)
    builder.add_node("extract_logic", extract_logic_node)
    builder.add_node("extract_auth", extract_auth_node)
    builder.add_node("extract_db_schema", extract_db_data_node)
    builder.add_node("project_setup", setup_node)

    builder.set_entry_point("extract_api")
    builder.add_edge("extract_api", "extract_logic")
    builder.add_edge("extract_logic", "extract_auth")
    builder.add_edge("extract_auth", "extract_db_schema")  
    builder.add_edge("extract_db_schema","project_setup")
    builder.set_finish_point("project_setup")

    return builder.compile()