from utils.groq_llm import llama3_chat

def extract_logic_node(state):
    prompt = f"""From the following SRS, extract business rules and backend logic(e.g. computations, workflows). Respond in JSON format.
    Do not generate answers from general knowledge. If no logic is present, respond with "No business logic found".
    Just extract the business logic, do not include any other information and give json only dont add any other text.
    API Definitions:
    {state['api_endpoints']}
    """

    res = llama3_chat(prompt)
    return {"business_logic": res, **state}