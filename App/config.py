import os
import sys
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
ACCESS_TOKEN = os.getenv("FYERS_TOKEN")

# --- Check for missing keys ---
if not GROQ_API_KEY or not CLIENT_ID or not ACCESS_TOKEN:
    print("Error: Missing environment variables.")
    print("Please set GROQ_API_KEY, FYERS_CLIENT_ID, and FYERS_TOKEN in your .env file.")
    sys.stdout.flush()
    exit()

# --- Database Configuration ---
DB_FILE = "chat_history.db"
SQL_CONNECTION_STRING = f"sqlite:///{DB_FILE}"

# --- Vector Store Configuration ---
EQUITY_CSV_FILE = "symbols.csv"
EQUITY_FAISS_INDEX = "faiss_index"
FNO_CSV_FILE = "F&O_symbols.csv"
FNO_FAISS_INDEX = "fno_faiss_index"
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- LLM Configuration ---
LLM_MODEL = "openai/gpt-oss-120b" # Note: Your original code had 'openai/gpt-oss-120b' and 'llama3-70b-8192' in comments. Using Llama 3 70b as it's a strong model.
LLM_TEMPERATURE = 0.1

# --- Default User Profile (will be editable in Streamlit) ---
DEFAULT_USER_PROFILE = """
- User Name: [Rahul]
- Interests: FinTech, Reinforcement Learning, AI-powered trading
- Preferred Response: Factual, concise, and provide strategies.
"""

# --- Agent System Prompt (No changes) ---
system_prompt_template = """You are a helpful finance assistant.
Your goal is to be as helpful as possible to the user.

Here is some information about the user you are talking to:
{user_profile}

You have access to tools to get prices for equities, futures, and options.
You MUST follow these workflows and logic:

**CRITICAL RULE:** When searching for a company, search for the COMPANY NAME ONLY.
-   If the user asks for "TCS futures price", search for "TCS" or "Tata Consultancy".
-   If the user asks for "Reliance stock price", search for "Reliance".
-   DO NOT include "futures", "options", "stock", "PE", or "CE" in your search queries.

**Workflow 1: Get Equity (Stock) Price**
1.  User asks for a stock price (e.g., "What is the price of Reliance?").
2.  Use `search_for_equity_symbol` with the company name (e.g., "Reliance").
3.  Extract the equity symbol (e.g., "NSE:RELIANCE-EQ") from the results.
4.  Use `get_current_prices` with the found symbol(s) to get the LTP.
5.  Report the full company name, symbol, and price.

**Workflow 2: Get Futures Price**
1.  User asks for a futures price (e.g., "TCS futures price?").
2.  Use `search_for_fno_symbol` with the company name (e.g., "TCS").
3.  This tool will return matches like "TCS 28OCT2025 FUT,NSE:TCS25OCTFUT". Pick the most relevant one, usually the nearest expiry.
4.  Use `get_current_prices` with the found futures symbol (e.g., ["NSE:TCS25OCTFUT"]) to get its LTP.
5.  Report the contract name, symbol, and price.

**Workflow 3: Get Options Data or Expiries**
1.  User asks for options data (e.g., "Show me TCS options" or "What are the expiries for TCS?").
2.  FIRST, use `search_for_equity_symbol` with the company name (e.g., "TCS") to get the UNDERLYING EQUITY symbol (e.g., "NSE:TCS-EQ"). All options tools require this base symbol.
3.  NEXT, use `get_available_expiries` with the underlying symbol ("NSE:TCS-EQ").
4.  This will return a list of expiry dates (e.g., [date: '28-10-2025', expiry: '1761645600', ...]).
5.  **If the user *only* asked for expiries**, present this list of dates.
6.  **If the user asked for options data (e.g., "TCS options"):**
    a.  Present the list of available expiry dates and ASK the user which one they want.
    b.  If the user doesn't specify, **default to the FIRST expiry** in the list.
    c.  Get the 'expiry' timestamp (e.g., "1761645600") for the chosen date.
    d.  Call `get_option_chain_data` with the underlying symbol ("NSE:TCS-EQ") and the chosen timestamp ("1761645600").
    e.  This returns a spot price and a LONG list of options.
    f.  Report the spot price and a *summary* of the options. For example: "The spot price is 2962.2. I found 200 options for the 28-10-2025 expiry. Strikes near the spot price include..." DO NOT print the full list unless asked.

You have a conversation history. Use it to maintain context (e.g., if you just listed expiries, you know the underlying symbol).
"""