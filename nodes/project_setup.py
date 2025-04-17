from utils.groq_llm import llama3_chat
import json
import re

def setup_node(state):
    api_endpoints = state.get("api_endpoints", "")
    business_logic = state.get("business_logic", "")
    auth_requirements = state.get("auth_requirements", "")  
    db_schema = state.get("db_schema", "")

    prompt = f"""
    Based on the following project analysis, generate the complete initial FastAPI project structure in JSON format.
    Just give structure in response, do not include any other information and give json only dont add any other text.
    Dont create tables in database if they already exist in the database.

    The JSON should include:
    - Folder structure with nested directories and files
    - File names as keys and their content as values
    - Include a "requirements.txt" file with necessary dependencies
    - Include a "setup.sh" script for setting up the environment
 
    Below is the format of response other than this you should not add any other text.
    The response should be in JSON format.
    Example JSON format:
    {{
        "app/": {{
            "routers/": {{
                "user.py": "content of user.py",
                "item.py": "content of item.py"
            }},
            "models/": {{
                "user.py": "content of user.py",
                "item.py": "content of item.py"
            }},
            "__init__.py": "content of __init__.py",
            "main.py": "content of main.py"
        }},
        "requirements.txt": "fastapi\\nuvicorn\\npsycopg2-binary\\nalembic\\nsqlalchemy\\npython-dotenv",
        "setup.sh": "content of setup.sh"
    }}

    Format of Folder should be like this:
    project_root/
│── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── user.py
│   │   │   ├── item.py
│   │   │   └── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── item.py
│   │   └── __init__.py
│   ├── services/
│   ├── database.py
│   ├── main.py
│── tests/
│── Dockerfile
│── requirements.txt
│── .env
│── README.md
 
    API Definitions:
    {api_endpoints}
    BUSINESS LOGIC:
    {business_logic}
    AUTHENTICATION AND AUTHORIZATION:
    {auth_requirements}
    DATABASE SCHEMA:
    {db_schema}

    """
    res = llama3_chat(prompt)
    
    # Clean up the response to extract the actual JSON
    cleaned_json = extract_json_from_text(res)
    
    return {"setup": cleaned_json, **state}

def extract_json_from_text(text):
    """Extract valid JSON from text that may contain markdown or other content"""
    # Try to parse directly first
    try:
        json.loads(text)
        return text  # If it parses correctly, return as is
    except json.JSONDecodeError:
        pass
    
    # Look for JSON pattern within code blocks
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, text)
    if match:
        json_content = match.group(1)
        try:
            # Validate that this is valid JSON
            json.loads(json_content)
            return json_content
        except json.JSONDecodeError:
            pass
    
    # If no code block, look for curly braces pattern
    json_pattern = r'(\{[\s\S]*\})'
    match = re.search(json_pattern, text)
    if match:
        json_content = match.group(1)
        try:
            # Validate that this is valid JSON
            json.loads(json_content)
            return json_content
        except json.JSONDecodeError:
            pass
    
    # If all else fails, just return the original text and let the caller handle errors
    return text