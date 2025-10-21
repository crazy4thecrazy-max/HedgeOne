import streamlit as st
import io
from contextlib import redirect_stdout
from langchain_community.chat_message_histories import SQLChatMessageHistory

# --- Local Imports ---
from config import SQL_CONNECTION_STRING, DEFAULT_USER_PROFILE
from db_utils import init_db, get_threads, create_thread
from agent import get_agent_executor

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Hedge One AI Assistant")

# --- Database Initialization ---
# This runs once at the start of the app
init_db()

# --- Helper function to load chat history for display ---
def load_chat_history(session_id):
    """Loads chat history from DB and formats it for Streamlit display."""
    history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string=SQL_CONNECTION_STRING
    )
    messages = []
    for msg in history.messages:
        role = "user" if msg.type == "human" else "assistant"
        messages.append({"role": role, "content": msg.content})
    return messages

# --- Sidebar ---
with st.sidebar:
    st.title("Hedge One")
    st.markdown("---")

    # --- Profile Section ---
    st.header("Your Profile")
    st.session_state.user_profile = st.text_area(
        "Edit your info for the AI",
        value=st.session_state.get("user_profile", DEFAULT_USER_PROFILE),
        height=150,
        help="The AI will use this information to personalize its responses."
    )
    st.markdown("---")

    # --- New Chat Section ---
    st.header("Chat Threads")
    new_chat_name = st.text_input("New Chat Name", placeholder="e.g., 'Options Strategy'")
    
    if st.button("Start New Chat"):
        if new_chat_name:
            session_id = create_thread(new_chat_name)
            if session_id:
                st.session_state.session_id = session_id
                st.session_state.messages = [] # Clear messages for new chat
                st.rerun()
        else:
            st.error("Please enter a name for the chat.")

    # --- Existing Chats Section ---
    st.subheader("Existing Chats")
    threads = get_threads()  # Gets {session_id: thread_name}
    
    if not threads:
        st.write("No chats yet.")
    else:
        for session_id, thread_name in threads.items():
            if st.button(thread_name, key=session_id, use_container_width=True):
                st.session_state.session_id = session_id
                # Load history for display
                st.session_state.messages = load_chat_history(session_id)
                st.rerun()

# --- Main Chat Interface ---
st.title("AI Financial Assistant")

# Check if a chat is selected
if "session_id" not in st.session_state:
    st.info("Start a new chat or select an existing one from the sidebar to begin.")
    st.stop()

# A session is active
session_id = st.session_state.session_id
user_profile = st.session_state.user_profile

# Get the session-specific agent
# We cache this to avoid re-creating it on every single widget interaction
@st.cache_resource(ttl=3600)
def get_cached_agent(session_id, user_profile):
    return get_agent_executor(session_id, user_profile)

try:
    agent_exec = get_cached_agent(session_id, user_profile)
except Exception as e:
    st.error(f"Error loading agent. Your API keys may be invalid. Error: {e}")
    st.stop()


# Initialize or load messages for display
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history(session_id)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about stocks, futures, or options..."):
    # Add user message to display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Capture verbose output from the agent
            f = io.StringIO()
            with redirect_stdout(f):
                try:
                    response = agent_exec.invoke({"input": prompt})
                    output = response['output']
                except Exception as e:
                    output = f"An error occurred: {e}"
            
            agent_steps = f.getvalue() # Get the captured stdout
            
            # Display the final output
            st.markdown(output)
            
            # Add agent steps to an expander
            with st.expander("See agent's thought process"):
                st.code(agent_steps)

    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": output})