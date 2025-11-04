import os
import autogen
import json
import logging
import sqlalchemy
from typing import Annotated, Optional

# --- 1. IMPORT YOUR REAL CODE & TOOLS MODULE ---
import validation_module
import build_md
import tools  # We need this for the new get_tables tool
from dotenv import load_dotenv

# --- 2. CONFIGURE LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 3. LOAD CONFIG ---
load_dotenv()
API_VERSION = os.getenv("API_VERSION", "2024-02-01") # Added default
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT") 
API_KEY = os.getenv("API_KEY") 
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gpt-4.1-nano") # Added default/getter

config_list = [
    {
        "model": DEPLOYMENT_NAME,
        "api_key": API_KEY,
        "base_url": AZURE_ENDPOINT,
        "api_type": "azure",
        "api_version": API_VERSION,
    }
]

llm_config = {
    "config_list": config_list,
    "cache_seed": 42,
    "timeout": 300, # Increased for long validation
}

# --- 4. TOOL DEFINITIONS ---
# This is our connection string, hardcoded for the POC
DB_URL = "sqlite:///database/sample_data.db"

# TOOL 1: Your friend's profiler (placeholder)
def run_data_profiling(
    file_path: Annotated[str, "The file path to the CSV or Excel file"]
) -> Annotated[str, "The JSON string result of the data profiling"]:
    """Runs a data profiling process on the available data."""
    logging.info(f"... EXECUTING: profiler('{file_path}')...")
    result = {
        "file_name": file_path, "total_rows": 5000, "total_columns": 10,
        "column_stats": {"OrderID": {"nulls": 50}, "Email": {"nulls": 120}}
    }
    return json.dumps(result)

# TOOL 2: Our Schema Validator (from validation_module.py)
def run_schema_validation(
    file_path: Annotated[str, "The file path to the CSV or Excel file"],
    table_name: Annotated[str, "The target database table name (e.g., 'customer_orders')"]
) -> Annotated[str, "The FULL JSON string result of the schema validation"]:
    """Runs the full schema validation process on a file against a specific table."""
    logging.info(f"... EXECUTING: run_schema_validation('{file_path}', '{table_name}')...")
    try:
        final_report_dict = validation_module.run_multi_sheet_validation(
            file_path=file_path,
            db_url=DB_URL,
            user_provided_table_name=table_name
        )
        return json.dumps(final_report_dict)
    except Exception as e:
        logging.error(f"... ERROR in run_schema_validation: {e}")
        return json.dumps({"error": str(e)})

# TOOL 3: Our Markdown Converter (from generate_markdown.py)
def convert_json_to_markdown(
    json_report_str: Annotated[str, "The JSON report string from a previous tool call"]
) -> Annotated[str, "A formatted Markdown report"]:
    """Converts a JSON report into a human-readable Markdown format."""
    logging.info(f"... EXECUTING: convert_json_to_markdown(...) ...")
    try:
        data = json.loads(json_report_str)
        markdown_report = build_md.create_validation_markdown(data)
        return markdown_report
    except Exception as e:
        logging.error(f"... ERROR in convert_json_to_markdown: {e}")
        return json.dumps({"error": str(e)})

# TOOL 4: (NEW) The key to our fluid conversation
def get_available_tables() -> Annotated[str, "A JSON list of available table names."]:
    """Retrieves a list of all available table names from the database."""
    logging.info(f"... EXECUTING: get_available_tables() ...")
    try:
        engine = sqlalchemy.create_engine(DB_URL)
        schemas = tools.get_all_table_schemas(engine)
        return json.dumps(list(schemas.keys()))
    except Exception as e:
        logging.error(f"... ERROR in get_available_tables: {e}")
        return json.dumps({"error": str(e)})

# --- 5. AGENT DEFINITIONS ---

# AGENT 1: The User
user_proxy = autogen.UserProxyAgent(
    name="User",
    # "TERMINATE" means it will auto-reply to tool calls,
    # but will STOP for human input if a message ends with "TERMINATE".
    human_input_mode="TERMINATE", 
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    system_message="""You are the user and code executor.
    You provide the file path and answer questions.
    When a tool is called, you execute it.
    You ONLY stop for input when a message ends with the word TERMINATE.""",
    
    # This agent will execute ALL tool calls
    code_execution_config={"work_dir": "autogen_work_dir", "use_docker": False}, 
)

## AGENT 2: The Conductor (The "C.T." Chatbot Brain)
conductor_agent = autogen.AssistantAgent(
    name="ConductorAgent",
    llm_config=llm_config,
    system_message="""You are the **Conductor**, the primary Data Steward assistant.
    Your job is to have a fluid, step-by-step conversation with the User.
    
    **YOUR GOAL:**
    1.  Greet the user and ask them what they want to do (e.g., "profile" or "validate").
    2.  Get all required arguments from the user (like `table_name` or `output_format`).
    3.  Call the correct specialist agent (`@DataProfilerAgent` or `@SchemaValidatorAgent`).
    4.  Get the final report, call `@MarkdownAgent` to format it, and show the user.
    
    **YOUR TOOLS:**
    - You can call `get_available_tables` *only if the user asks* for table options.
    
    **CRITICAL RULE:**
    - **ASK ONE QUESTION AT A TIME.**
    - When you need to ask the user a question, end your *entire* message with the single word `TERMINATE`.
    
    Example:
    "I can validate the schema. What is the target table name? TERMINATE"
    """
)

# AGENT 3: The Profiler (Specialist)
data_profiler_agent = autogen.AssistantAgent(
    name="DataProfilerAgent",
    llm_config=llm_config,
    system_message="""You are a silent specialist. Your only job is to call the `run_data_profiling` tool.
    Report the JSON result back to the `ConductorAgent`."""
)

# AGENT 4: The Validator (Specialist)
schema_validator_agent = autogen.AssistantAgent(
    name="SchemaValidatorAgent",
    llm_config=llm_config,
    system_message="""You are a silent specialist. Your only job is to call the `run_schema_validation` tool.
    If you get an error that the table name is missing, report the error back.
    Report the JSON result back to the `ConductorAgent`."""
)

# AGENT 5: The Markdown Formatter (Specialist)
markdown_agent = autogen.AssistantAgent(
    name="MarkdownAgent",
    llm_config=llm_config,
    system_message="""You are a silent specialist. Your only job is to call the `convert_json_to_markdown` tool.
    Report the Markdown string result back to the `ConductorAgent`."""
)
# --- 6. TOOL REGISTRATION ---
# We register each tool with its specific CALLER and the user_proxy as EXECUTOR.

autogen.register_function(
    get_available_tables,
    caller=conductor_agent,
    executor=user_proxy, # <-- FIX
    name="get_available_tables",
    description="Get a list of all tables in the database."
)

autogen.register_function(
    run_data_profiling,
    caller=data_profiler_agent,
    executor=user_proxy, # <-- FIX
    name="run_data_profiling",
    description="Run the data profiler tool."
)

autogen.register_function(
    run_schema_validation,
    caller=schema_validator_agent,
    executor=user_proxy, # <-- FIX
    name="run_schema_validation",
    description="Run the schema validator tool."
)

autogen.register_function(
    convert_json_to_markdown,
    caller=markdown_agent,
    executor=user_proxy, # <-- FIX
    name="convert_json_to_markdown",
    description="Convert a JSON report to Markdown."
)
# --- 7. GROUP CHAT SETUP ---
# We use 5 agents: User, Conductor, Profiler, Validator, Markdown
agents = [user_proxy, conductor_agent, data_profiler_agent, schema_validator_agent, markdown_agent]
group_chat = autogen.GroupChat(
    agents=agents,
    messages=[],
    max_round=50, # Increase max rounds for complex conversation
    speaker_selection_method="auto", # The manager will decide who speaks
    allow_repeat_speaker=True
)

# This manager is the "brain" that selects the next agent
# This manager is the "brain" that selects the next agent
manager = autogen.GroupChatManager(
    name="Orchestrator",
    groupchat=group_chat,
    llm_config=llm_config,
    # This system message is the "logic" of the chat
    system_message="""You are the Orchestrator. Your job is to select the next agent to speak.
    
    **THE FLOW (Follow this precisely):**
    
    1.  **After the `User` (human) speaks:** YOU MUST ALWAYS select the `ConductorAgent`.
    
    2.  **After a `Specialist` (`DataProfilerAgent`, `SchemaValidatorAgent`, `MarkdownAgent`) speaks:** YOU MUST ALWAYS select the `ConductorAgent`.
    
    3.  **After the `User` (as executor) posts a tool result (e.g., "***** Response from calling tool *****"):** YOU MUST ALWAYS select the `ConductorAgent`.
    
    4.  **After the `ConductorAgent` speaks:**
        a) If it called a specialist (e.g., "@DataProfilerAgent"), select that specialist.
        b) If it called a tool (e.g., `get_available_tables`), select the `User` (who is the executor).
        c) If it asked the user a question (ending in `TERMINATE`), select the `User` (who is the human).

    This flow ensures the `ConductorAgent` is the central brain.
    """
)
# --- 8. RUN THE CHAT ---
print("="*50)
print("🚀 STARTING CHAT")
print("Type 'exit' or 'terminate' to end the conversation.")
print("="*50)

# We provide the file path in the first message.
user_proxy.initiate_chat(
    manager,
    message="Hi, I have a file called 'new_orders.csv'. Can you help me with it?"
)