import sys
from langchain_core.tools import tool
from fyers_client import fyers  # Import the initialized Fyers model
from vector_store import equity_vectorstore, fno_vectorstore # Import loaded stores

# --- Tool Definitions (No changes) ---

@tool
def search_for_equity_symbol(company_query: str, top_k: int = 3) -> list[str]:
    """
    Searches the EQUITY vector database for the top_k (default 3) most similar
    company names for a given query.
    Returns a list of raw strings, where each string contains the
    'Company Name,Symbol' (e.g., "TATA CONSULTANCY SERV LT,NSE:TCS-EQ").
    This tool should be used to find the UNDERLYING EQUITY symbol for stocks
    and for getting options data.
    """
    print(f"[Tool Call] search_for_equity_symbol: Searching for '{company_query}', k={top_k}")
    sys.stdout.flush()
    try:
        docs = equity_vectorstore.similarity_search(company_query, k=top_k)
        if not docs:
            return ["Error: No equity symbols found matching that query."]
        results = [doc.page_content for doc in docs]
        print(f"[Tool Result] Found matches: {results}")
        sys.stdout.flush()
        return results
    except Exception as e:
        print(f"[Tool Error] {e}")
        sys.stdout.flush()
        return [f"Error during equity search: {e}"]

# ... (imports and other tools are unchanged) ...

@tool
def search_for_fno_symbol(derivative_query: str, top_k: int = 3) -> list[str]:
    """
    Searches the F&O (Futures & Options) vector database for F&O-enabled
    equities.
    Returns a list of raw strings, where each string contains the
    'Company Name,Equity Symbol,Lot Size' 
    (e.g., "ADANI ENTERPRISES,NSE:ADANIENT-EQ,300").
    This tool should be used to find the UNDERLYING EQUITY symbol for
    derivatives (Options/Futures) AND to find its lot size.
    """
    print(f"[Tool Call] search_for_fno_symbol: Searching for '{derivative_query}', k={top_k}")
    sys.stdout.flush()
    try:
        docs = fno_vectorstore.similarity_search(derivative_query, k=top_k)
        if not docs:
            return ["Error: No F&O symbols found matching that query."]
        results = [doc.page_content for doc in docs]
        print(f"[Tool Result] Found matches: {results}")
        sys.stdout.flush()
        return results
    except Exception as e:
        print(f"[Tool Error] {e}")
        sys.stdout.flush()
        return [f"Error during F&O search: {e}"]

@tool
def get_current_prices(symbols: list[str]) -> dict:
    """
    Fetches the current last traded price (LTP) for a list of one or more
    valid trading symbols (e.g., ["NSE:RELIANCE-EQ", "NSE:TCS25OCTFUT"]).
    This works for both equities and futures.
    Returns a dictionary where keys are symbols and values are their prices.
    """
    print(f"[Tool Call] get_current_prices: Fetching for {symbols}")
    sys.stdout.flush()
    if not symbols:
        return {"Error": "No symbols provided."}
    
    symbol_string = ",".join(symbols)
    data = {"symbols": symbol_string}
    
    try:
        response = fyers.quotes(data)
        if response.get("s") != "ok":
            print(f"[Tool Error] Fyers API error: {response.get('message')}")
            sys.stdout.flush()
            return {"Error": f"Fyers API error: {response.get('message')}"}
        
        price_results = {}
        if "d" in response and response["d"]:
            for item in response["d"]:
                symbol_name = item.get("n")
                last_price = item.get("v", {}).get("lp")
                if symbol_name and last_price is not None:
                    price_results[symbol_name] = last_price
            print(f"[Tool Result] Prices: {price_results}")
            sys.stdout.flush()
            return price_results
        else:
            print("[Tool Error] No 'd' key in Fyers response.")
            sys.stdout.flush()
            return {"Error": "No price data returned from Fyers."}
    except Exception as e:
        print(f"[Tool Error] {e}")
        sys.stdout.flush()
        return {"Error": f"Exception while calling Fyers API: {e}"}

@tool
def get_available_expiries(underlying_symbol: str) -> dict:
    """
    Fetches all available option expiry dates for a given UNDERLYING EQUITY symbol
    (e.g., "NSE:TCS-EQ").
    Returns a dictionary containing a list of expiry data.
    """
    print(f"[Tool Call] get_available_expiries: Fetching for {underlying_symbol}")
    sys.stdout.flush()
    data = {"symbol": underlying_symbol}
    try:
        response = fyers.optionchain(data=data)
        if response.get("s") != "ok":
            print(f"[Tool Error] Fyers API error: {response.get('message')}")
            sys.stdout.flush()
            return {"Error": f"Fyers API error: {response.get('message')}"}
        
        expiry_data = response.get("data", {}).get("expiryData", [])
        if not expiry_data:
            return {"Error": "No expiry data found for this symbol."}
            
        print(f"[Tool Result] Found {len(expiry_data)} expiries.")
        sys.stdout.flush()
        return {"expiryData": expiry_data}
        
    except Exception as e:
        print(f"[Tool Error] {e}")
        sys.stdout.flush()
        return {"Error": f"Exception while calling Fyers API: {e}"}

@tool
def get_option_chain_data(underlying_symbol: str, expiry_timestamp: str) -> dict:
    """
    Fetches the complete option chain for a given UNDERLYING EQUITY symbol
    (e.g., "NSE:TCS-EQ") and a specific expiry timestamp (e.g., "1761645600").
    The timestamp MUST be one of the 'expiry' values from 'get_available_expiries'.
    Returns a dictionary with the spot price and a list of tuples:
    (strike_price, premium_ltp, option_type 'CE'/'PE').
    """
    print(f"[Tool Call] get_option_chain_data: Fetching for {underlying_symbol} at {expiry_timestamp}")
    sys.stdout.flush()
    data = {"symbol": underlying_symbol, "timestamp": expiry_timestamp}
    try:
        response = fyers.optionchain(data=data)
        if response.get("s") != "ok":
            print(f"[Tool Error] Fyers API error: {response.get('message')}")
            sys.stdout.flush()
            return {"Error": f"Fyers API error: {response.get('message')}"}

        options_chain_list = response.get("data", {}).get("optionsChain", [])
        if not options_chain_list:
            return {"Error": "No option chain data found for this symbol and expiry."}

        spot_price = options_chain_list[0].get("ltp")

        options_list = []
        for item in options_chain_list[1:]:
            strike = item.get("strike_price")
            ltp = item.get("ltp")
            opt_type = item.get("option_type")
            if strike is not None and ltp is not None and opt_type in ('CE', 'PE'):
                options_list.append((strike, ltp, opt_type))
        
        result = {
            "spot_price": spot_price,
            "options": options_list
        }
        print(f"[Tool Result] Found spot price {spot_price} and {len(options_list)} options.")
        sys.stdout.flush()
        return result

    except Exception as e:
        print(f"[Tool Error] {e}")
        sys.stdout.flush()
        return {"Error": f"Exception while calling Fyers API: {e}"}

# --- Exportable list of all tools ---
tools = [
    search_for_equity_symbol, 
    search_for_fno_symbol,
    get_current_prices,
    get_available_expiries,
    get_option_chain_data
]

print("Tools defined.")
sys.stdout.flush()