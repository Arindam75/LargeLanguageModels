from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import os

load_dotenv()
#api_key = os.getenv("OPENAI_API_KEY")

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")


##  langchain api https://api.python.langchain.com/
##  video link https://www.youtube.com/watch?v=YqqRkuizNN4&t=11s
##  currently at 40:56

## Initiate the Database connection when the end user presses
## th connect button   
def init_database_connection(host_name, user_name, user_password, db_name, port) -> SQLDatabase:

    db_uri = f"mysql+mysqlconnector://{user_name}:{user_password}@{host_name}:{port}/{db_name}"
    return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
    template = """
    You are a data analyst at a company. You are interacting with a user, asking question about the company's database.
    Based on the table schema below , write a SQL query that would answer the user question. Take the conversation history into account.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History:{chat_history}

    Write only the SQL query and nothing else. Do not wrap the sql query in any other text, not even backticks.

    For example:
    Question: which 3 artists have the most tracks?
    SQL Query: Select ArtistId, COUNT(*) as track_count FROM Track, GROUP By ArtistId ORDER BY track_count DESC LIMIT 3;
    Question: Name 10 artists
    SQL Query: Select Name FROM Artist ORDER BY Name LIMIT 10;

    Your Turn:

    Question: {question}
    SQL Query:
    """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(model = "gpt-4-0125-preview")

    def get_schema(_):
        return db.get_table_info()

    return (
        RunnablePassthrough.assign(schema = get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)
    
    template =  """
    You are a data analyst at a company. You are interacting with a user, asking question about the company's database.
    Based on the table schema below , question, sql query and sql reponse, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History:{chat_history}
    SQL Query: <SQL>{query}</SQL>
    User Question: {question}
    SQL Response: {response}
    """


    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model = "gpt-4-0125-preview")

    chain = (
        RunnablePassthrough.assign(query =  sql_chain).assign(
        schema = lambda _:db.get_table_info(),
        response = lambda vars: db.run(vars["query"])
        )
        | prompt
        | llm
        | StrOutputParser()
        )

    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })

##_________________________________________
## Initiate a variable to hold chat history 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content = "Hello ! I'm a SQL Assistant, Ask me anything about your database")]

## Setting Up Streamlit Frontend
st.set_page_config(page_title = "Chat with MySQL", page_icon=":speech_balloon: ")
st.title("Chat with MySQL")

## Sidebar Settings
with st.sidebar:
    st.title("Settings")
    st.write("Enter your MySQL credentials here")

    st.text_input("Host", value = "localhost",key="Host")
    st.text_input("Port", value = "3306", key="Port")
    st.text_input("Username", value = "root", key="Username")
    st.text_input("Password", type = "password", value = "mydatabase", key="Password")
    st.text_input("Database", value = "chinook", key="Database")

    if st.button("Connect"):
        with st.spinner("Connecting to databse ...."):
            db = init_database_connection(
                st.session_state["Host"],
                st.session_state["Username"],
                st.session_state["Password"],
                st.session_state["Database"],
                st.session_state["Port"]
            )
            st.session_state.db = db
            st.success("Connected!")

## Display Chat History
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a Message ....")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
    
    st.session_state.chat_history.append(AIMessage(content=response))
#st.chat_input("Type a Message ....")