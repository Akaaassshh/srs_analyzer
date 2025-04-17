from utils.groq_llm import llama3_chat
import json
import re

def extract_logic_node(state):
    prompt = f"""From the following SRS, extract business rules and backend logic(e.g. computations, workflows). Respond in JSON format.
    Do not generate answers from general knowledge. If no logic is present, respond with "No business logic found".
    Just extract the business logic, do not include any other information and give json only dont add any other text.
    
    SRS:
    {state.get('srs_text', '')}
    
    API Definitions:
    {state['api_endpoints']}
    """

    res = llama3_chat(prompt)
    
    # Clean up the response to extract the actual JSON
    cleaned_json = extract_json_from_text(res)
    
    return {"business_logic": cleaned_json, **state}

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