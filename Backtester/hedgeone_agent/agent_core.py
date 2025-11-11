# LangChain (modern)
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Import from our package
from .config import GROQ_API_KEY
from .agent_tools import strategy_search, symbol_search, run_strategy_backtest


# --- Helper to robustly call runnables / agents across versions ---
def invoke_runnable(runnable, input_obj):
    """
    Try common ways to call a LangChain runnable/agent across versions.
    Returns output or raises the last exception.
    """
    last_exc = None
    try:
        # Preferred: modern .invoke API
        return runnable.invoke(input_obj)
    except Exception as e:
        last_exc = e
    try:
        # Fallback: .run
        return runnable.run(input_obj)
    except Exception as e:
        last_exc = e
    try:
        # Fallback: direct call (some runnables are callables)
        return runnable(input_obj)
    except Exception as e:
        last_exc = e
    raise last_exc

# --- 9. AGENT CREATION (Using create_agent) ---
def create_agent_runnable():
    """Creates the main LangChain tool-calling agent (runnable)."""

    llm = ChatGroq(
        model="openai/gpt-oss-120b", # Using a more powerful model for better tool use
        temperature=0,
        api_key=GROQ_API_KEY
    )

    # Tools are imported from agent_tools.py
    tools = [strategy_search, symbol_search, run_strategy_backtest]

    # ✅ Use `system_prompt` instead of custom ChatPromptTemplate
    system_prompt = (
        "You are a helpful and conversational financial analyst chatbot. "
        "Your goal is to help the user backtest trading strategies.\n\n"
        "Here is your workflow:\n"
        "1. Greet the user.\n"
        "2. If the user asks to backtest a strategy (e.g., 'backtest a golden cross on Reliance'):\n"
        "   a. First, use the `strategy_search` tool to find the `strategy_id` and its parameters (e.g., from 'golden cross').\n"
        "   b. Next, check if the user provided an exact symbol (like 'NSE:RELIANCE-EQ') or a company name (like 'Reliance').\n"
        "   c. **If they provided a company name**, you MUST use the `symbol_search` tool to find the top 3 matches.\n"
        "   d. **Show these 3 matches** to the user (e.g., 'I found: 1. Reliance Industries (NSE:RELIANCE-EQ), ...') and ask them to confirm which symbol they want to use. You cannot proceed without their confirmation.\n"
        "   e. Politely ask for ALL other missing information: the exact symbol (if not confirmed), start date, end date, and any strategy parameter values (like n1, n2).\n"
        "   f. For `MultiInstrumentSignal`, ask for the list of signal symbols AND the single trade symbol.\n"
        "3. **Only when you have 100% of the information** (the exact `strategy_id`, all exact `symbols`, `start_date`, `end_date`, and `params_dict`) call the `run_strategy_backtest` tool ONCE.\n"
        "4. Present the results clearly."
    )


    # ✅ New API syntax — `prompt` replaced by `system_prompt`
    agent_runnable = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    return agent_runnable