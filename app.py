import streamlit as st

from applications.pdf_chat import create_db_from_pdf, get_response_from_query_pdf
from applications.sql_db_chat import create_db_from_uri, get_response_from_query_sql
from applications.youtube_chat import create_db_from_youtube_url, get_response_from_query_youtube

st.title("💬 Chat With Your Data 📝️")
st.write("This is a simple app to chat with your data.")

# Input the OpenAI API key
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not api_key:
    st.info("Please add your OpenAI API key to continue")
    st.stop()

# Select the application
applications = ["PDF Chat", "SQL Database Chat", "YouTube Chat"]
selected_application = st.sidebar.selectbox("Select an application", applications)

# Creating the database
if applications.index(selected_application) == 0:
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"], accept_multiple_files=True)
    if not pdf_file:
        st.info("Please upload a PDF file to continue.")
        st.stop()
    else:
        db = create_db_from_pdf(pdf_file, api_key)
elif applications.index(selected_application) == 1:
    selected_database = st.sidebar.radio("Select a database", ["Use my own database", "Use the sample database: Chinook", "Use Snowflake"])
    
    if selected_database == "Use my own database":
        database_uri = st.text_input("Database URI")
        if not database_uri:
            st.info("Please add a database URI to continue.")
            st.stop()
    elif selected_database == "Use the sample database: Chinook":
        database_uri = "sqlite:///sample_data/Chinook.db"
    elif selected_database == "Use Snowflake":
        user = st.sidebar.text_input("Snowflake User")
        password = st.sidebar.text_input("Snowflake Password", type="password")
        account = st.sidebar.text_input("Snowflake Account")
        database = st.sidebar.text_input("Snowflake Database")
        schema = st.sidebar.text_input("Snowflake Schema")
        warehouse = st.sidebar.text_input("Snowflake Warehouse")
        role = st.sidebar.text_input("Snowflake Role")
        
        if not (user and password and account and database and schema and warehouse and role):
            st.info("Please provide all Snowflake connection details to continue.")
            st.stop()
        else:
            database_uri = f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}"
    
    db = create_db_from_uri(database_uri)
elif applications.index(selected_application) == 2:
    video_url = st.text_input("YouTube Video URL")
    if not video_url:
        st.info("Please add a YouTube video URL to continue.")
        st.stop()
    else:
        db = create_db_from_youtube_url(video_url, api_key)

# Creating the chat interface
if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about your data!"}]

for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])

if prompt := st.chat_input(placeholder="Ask me anything about your data!"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        if applications.index(selected_application) == 0:
            response = get_response_from_query_pdf(prompt, db, api_key)
        elif applications.index(selected_application) == 1:
            response = get_response_from_query_sql(prompt, db, api_key)
        elif applications.index(selected_application) == 2:
            response = get_response_from_query_youtube(prompt, db, api_key)
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.write(response)
