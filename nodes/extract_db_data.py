from utils.groq_llm import llama3_chat

def extract_db_data_node(state):
    prompt = f"""From the following SRS, extract all the database schema: tables, columns, and relationships. Respond in JSON format.
    Do not generate answers from general knowledge. If no database schema is present, respond with "No database schema found".
    Just extract the database schema, do not include any other information and give json only dont add any other text.
    SRS:
    {state['srs_text']}

    API Definitions:
    {state['api_endpoints']}

    Business Logic:
    {state['business_logic']}

    """

    res = llama3_chat(prompt)
    return {"db_schema": res, **state}