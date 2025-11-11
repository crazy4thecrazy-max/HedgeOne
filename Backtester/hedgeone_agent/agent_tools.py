import json
from typing import List, Dict, Any
from langchain.tools import tool

# Import our package's functions and retrievers
from .rag_setup import get_strategy_retriever, get_symbol_retriever
from .data_provider import get_historical_data
from .backtest_engine import run_backtest_internal

# --- 8. LANGCHAIN AGENT TOOLS (@tool) ---
# Initialize retrievers globally
strategy_retriever = get_strategy_retriever()
symbol_retriever = get_symbol_retriever()


@tool
def strategy_search(query: str) -> dict:
    """
    Searches the strategy database to find the best strategy_id and its
    required parameters based on a user's description (e.g., 'golden cross').
    """
    print(f"--- RAG: Searching for query: '{query}' ---")
    try:
        # Use modern retriever invocation if available, fallback to get_relevant_documents
        results = None
        try:
            results = strategy_retriever.invoke(query)
        except Exception:
            try:
                results = strategy_retriever.get_relevant_documents(query)
            except Exception:
                results = strategy_retriever.similarity_search(query, k=1)
        if not results:
            return {"error": "No matching strategy found."}
        
        doc = results[0]
        metadata = dict(doc.metadata) if hasattr(doc, "metadata") else dict(doc)
        if isinstance(metadata.get("parameters"), str):
            metadata["parameters"] = json.loads(metadata["parameters"])
        
        print(f"--- RAG: Found strategy: {metadata.get('strategy_id', 'UNKNOWN')} ---")
        return metadata
    except Exception as e:
        return {"error": f"Error during strategy search: {e}"}

@tool
def symbol_search(company_name_query: str) -> List[Dict[str, str]]:
    """
    Searches the stock symbol database for a company name.
    Returns the top 3 potential matches (company name and symbol).
    """
    print(f"--- Symbol RAG: Searching for query: '{company_name_query}' ---")
    try:
        # Use modern retriever invocation
        results = symbol_retriever.invoke(company_name_query)
        
        matches = []
        if not results:
             print("--- Symbol RAG: No matches found. ---")
             return []
             
        for doc in results:
            # Extract from metadata, which is cleaner
            name = doc.metadata.get('company_name', 'N/A')
            symbol = doc.metadata.get('symbol', 'N/A')
            if name != 'N/A' and symbol != 'N/A':
                matches.append({"company_name": name, "symbol": symbol})
        
        print(f"--- Symbol RAG: Found matches: {matches} ---")
        return matches
    except Exception as e:
        print(f"--- Symbol RAG: Error: {e} ---")
        return [{"error": f"Error during symbol search: {e}"}]

@tool
def run_strategy_backtest(
    strategy_id: str, 
    symbols: List[str], 
    start_date: str, 
    end_date: str, 
    params_dict: Dict[str, Any]
) -> str:
    """
    Runs the final backtest. This tool should only be called when all 
    information (strategy_id, symbols, dates, and parameters) is collected.
    """
    print(f"--- Tool: run_strategy_backtest called for {strategy_id} ---")
    
    data_feeds = []
    for symbol in symbols:
        df = get_historical_data(symbol, start_date, end_date)
        if df.empty:
            return f"Error: Could not fetch data for symbol {symbol}."
        data_feeds.append(df)
        
    result_str = run_backtest_internal(
        strategy_id=strategy_id,
        data_feeds=data_feeds,
        params_dict=params_dict
    )
    return result_str