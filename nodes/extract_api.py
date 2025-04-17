from utils.groq_llm import llama3_chat

def extract_api_node(state):
    prompt = f"""From the following SRS,extract all the REST API endpoints with HTTP method, path, and parameter.Respond in JSON format.
    Just extract the API endpoints, do not include any other information and give json only dont add any other text.
    SRS:
    {state['srs_text']}
    """

    res = llama3_chat(prompt)
    return {"api_endpoints": res, **state}

