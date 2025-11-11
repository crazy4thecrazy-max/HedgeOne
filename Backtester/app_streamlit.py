import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# Add the package to the Python path
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import from our agent package
from hedgeone_agent.agent_core import create_agent_runnable
from hedgeone_agent.rag_setup import get_strategy_retriever, get_symbol_retriever
from hedgeone_agent.config import GROQ_API_KEY, FYERS_CLIENT_ID, FYERS_TOKEN

# --- Page Setup ---
st.set_page_config(
    page_title="HedgeOne Agent",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 HedgeOne Agent")
st.caption("A conversational bot for backtesting trading strategies.")

# --- Initialization (runs once) ---
@st.cache_resource
def initialize_agent():
    """Initializes RAG retrievers and the agent."""
    
    # Check for API keys
    if not (GROQ_API_KEY and FYERS_CLIENT_ID and FYERS_TOKEN):
        st.error("Error: Missing API keys in .env file.")
        st.error("Please ensure GROQ_API_KEY, FYERS_CLIENT_ID, and FYERS_TOKEN are set.")
        return None, "API keys missing."

    try:
        print("Initializing retrievers for Streamlit...")
        _ = get_strategy_retriever()
        _ = get_symbol_retriever()
        print("Retrievers ready.")
    except Exception as e:
        st.error(f"Error initializing RAG retrievers: {e}")
        st.error("Please ensure 'symbols.csv' exists and you have write permissions.")
        return None, str(e)
    
    try:
        agent_runnable = create_agent_runnable()
        print("Agent created.")
        return agent_runnable, None
    except Exception as e:
        st.error(f"Error creating agent: {e}")
        return None, str(e)

# Initialize agent and retrievers
agent_runnable, error = initialize_agent()

# --- Chat History Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Agent Response ---
if agent_runnable:
    if prompt := st.chat_input("Ask about a strategy..."):
        # Add user message to session state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare agent input
        agent_history = []
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                agent_history.append(HumanMessage(content=msg['content']))
            else:
                agent_history.append(AIMessage(content=msg['content']))
        
        # The prompt is the last message, already in agent_history
        input_obj = {"messages": agent_history}

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = agent_runnable.invoke(input_obj)
                    
                    # Extract output
                    if isinstance(response, dict):
                        output = response['messages'][-1].content
                    else:
                        output = str(response)
                    
                    st.markdown(output)
                    st.session_state.messages.append({"role": "assistant", "content": output})

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
else:
    st.error(f"Failed to initialize chatbot. Please check the error: {error}")
    st.stop()