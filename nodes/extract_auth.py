from utils.groq_llm import llama3_chat

def extract_auth_node(state):
    prompt = f"""Extract authentication and authorization methods from the following SRS. Use JSON format for the response.
        Just extract the authentication and authorization methods, do not include any other information and give json only dont add any other text.

    API Definitions:
    {state['api_endpoints']}
    Business Logic:
    {state['business_logic']}
    """

    res = llama3_chat(prompt)
    return {"auth_requirements": res, **state}

