from langchain_core.messages import HumanMessage, AIMessage

# Import from our package
from .config import GROQ_API_KEY, FYERS_CLIENT_ID, FYERS_TOKEN
from .agent_core import create_agent_runnable
from .rag_setup import get_strategy_retriever, get_symbol_retriever # To initialize them

# --- 10. MAIN CHAT LOOP ---
def main():
    """Main function to run the chatbot."""
    
    print("--- 🤖 HedgeOne Chatbot Initializing... ---")
    
    # Check for missing API keys
    if not (GROQ_API_KEY and FYERS_CLIENT_ID and FYERS_TOKEN):
        print("Error: Missing API keys in .env file.")
        print("Please ensure GROQ_API_KEY, FYERS_CLIENT_ID, and FYERS_TOKEN are set.")
        return

    # Initialize RAG retrievers
    print("Initializing retrievers...")
    try:
        # These functions (defined in Section 8) will create the stores if missing
        _ = get_strategy_retriever()
        _ = get_symbol_retriever()
        print("Retrievers ready.")
    except Exception as e:
        print(f"Error initializing retrievers: {e}")
        print("Please ensure 'symbols.csv' exists in the same directory and you have write permissions.")
        return
        
    agent_runnable = create_agent_runnable()
    chat_history = []

    print("Chatbot is ready! Type 'exit' to quit.")
    
    while True:
        try:
            query = input("You: ")
            print(f"\n\nYou: {query}")
            if query.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            # Build chat_history Messages for prompt
            agent_history = []
            for msg in chat_history:
                if msg['role'] == 'user':
                    agent_history.append(HumanMessage(content=msg['content']))
                else:
                    agent_history.append(AIMessage(content=msg['content']))

            # Input object to the agent; matches ChatPromptTemplate variables
            input_obj = {
                "messages": agent_history + [HumanMessage(content=query)]
            }

            # Use robust invoker helper (works across langchain releases)
            response = agent_runnable.invoke(input_obj) # <-- THIS IS THE 

            # Response handling varies by LLM/agent. We try to extract textual output robustly.
            output = None
            if isinstance(response, dict):
                output = response['messages'][-1].content # <-- THIS IS THE 
            else:
                output = str(response)

            chat_history.append({"role": "user", "content": query})
            chat_history.append({"role": "ai", "content": output})

            print(f"Chatbot: {output}")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()