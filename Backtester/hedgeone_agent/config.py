import os
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel

# --- 2. API & CONFIGURATION ---
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
FYERS_CLIENT_ID = os.environ.get("FYERS_CLIENT_ID")
FYERS_TOKEN = os.environ.get("FYERS_TOKEN")

# Global Fyers Model
fyers = fyersModel.FyersModel(
    client_id=FYERS_CLIENT_ID,
    token=FYERS_TOKEN,
    is_async=False,
    log_path=""
)

# Global RAG Config
STRATEGY_VECTOR_STORE_PATH = "faiss_index_strategies"
SYMBOL_VECTOR_STORE_PATH = "faiss_index_symbols"
SYMBOL_CSV_PATH = "symbols.csv"