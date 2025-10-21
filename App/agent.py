from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from llm import llm
from tools import tools
from config import SQL_CONNECTION_STRING, system_prompt_template

def get_agent_executor(session_id: str, user_profile: str) -> AgentExecutor:
    """
    Creates and returns a new AgentExecutor instance for a specific session_id.
    """
    
    # 1. Set up session-specific memory
    chat_history_backend = SQLChatMessageHistory(
        session_id=session_id,
        connection_string=SQL_CONNECTION_STRING
    )
    
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        chat_memory=chat_history_backend,
        max_token_limit=1000,
        memory_key="chat_history",
        return_messages=True
    )
    
    # 2. Create session-specific prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_template.format(user_profile=user_profile)),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # 3. Create session-specific agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        memory=memory,
        verbose=True  # We will capture this verbose output in Streamlit
    )
    
    return agent_executor