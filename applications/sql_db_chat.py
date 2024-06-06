from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

def create_db_from_uri(database_uri):
    return SQLDatabase.from_uri(database_uri)

def get_response_from_query_sql(prompt, db, api_key):
    llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=api_key, temperature=0)
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
    response = agent_executor.invoke(prompt)
    return response["output"]

def create_snowflake_db_from_input(user, password, account, database, schema, warehouse, role):
    database_uri = f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}"
    return create_db_from_uri(database_uri)