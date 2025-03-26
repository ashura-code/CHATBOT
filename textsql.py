from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from typing_extensions import TypedDict # for implementing types
from typing_extensions import Annotated
from langchain.chat_models import init_chat_model
from langchain import hub
from langgraph.graph import START, StateGraph
import getpass
import os




if not os.environ.get("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = ""
    os.environ["LANGSMITH_TRACING"] = "true"



db = SQLDatabase.from_uri("sqlite:///synthetic_vpc_logs.db")

class State(TypedDict): 
    question : str
    query : str
    result : str
    answer : str

#getpass.getpass("Enter API key for Groq: ")

if not os.environ.get("GROQ_API_KEY"):
  os.environ["GROQ_API_KEY"] = ""

llm = init_chat_model("gemma2-9b-it", model_provider="groq")

query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."] # type: ignore

def write_query(state: State):
    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 3,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result["query"]}

def execute_query(state: State):
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}

def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}


# main
graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)

graph_builder.add_edge(START, "write_query")


graph = graph_builder.compile()


for step in graph.stream(
    {"question": "what is the average rejection rate?"}, stream_mode="updates"
):
    print(step)