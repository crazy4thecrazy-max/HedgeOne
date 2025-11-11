import os
import json
import pandas as pd

# RAG / Vector Store
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

# Import constants from other modules in the package
from .strategies import STRATEGY_METADATA_LIST
from .config import STRATEGY_VECTOR_STORE_PATH, SYMBOL_VECTOR_STORE_PATH, SYMBOL_CSV_PATH

# --- 4. RAG SETUP FUNCTIONS ---
def create_strategy_vector_store():
    """
    Creates and saves a FAISS vector store from the strategy metadata.
    """
    print("Loading strategy metadata...")
    documents = []
    for strategy in STRATEGY_METADATA_LIST:
        content = f"Strategy: {strategy['strategy_id']}. Description: {strategy['description']}"
        metadata = {
            "strategy_id": strategy['strategy_id'],
            "description": strategy['description'],
            "parameters": json.dumps(strategy['parameters'])
        }
        documents.append(Document(page_content=content, metadata=metadata))
    
    print("Creating strategy embeddings... (This may take a moment on first run)")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(documents, embeddings)
    
    vector_store.save_local(STRATEGY_VECTOR_STORE_PATH)
    print(f"Strategy vector store saved to {STRATEGY_VECTOR_STORE_PATH}")

def get_strategy_retriever():
    """
    Loads the saved strategy FAISS vector store as a retriever.
    """
    if not os.path.exists(STRATEGY_VECTOR_STORE_PATH):
        print("Strategy vector store not found. Creating a new one...")
        create_strategy_vector_store()
        
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # allow_dangerous_deserialization kept for compatibility with older saved indexes
    vector_store = FAISS.load_local(STRATEGY_VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    return vector_store.as_retriever(search_kwargs={"k": 1})

def create_symbol_vector_store():
    """
    Creates and saves a FAISS vector store from the symbols.csv file.
    """
    if not os.path.exists(SYMBOL_CSV_PATH):
        print(f"Error: '{SYMBOL_CSV_PATH}' not found.")
        print("Please create this file with 'Company Name,Symbol' columns.")
        raise FileNotFoundError(f"Required file not found: {SYMBOL_CSV_PATH}")

    print(f"Loading {SYMBOL_CSV_PATH}...")
    try:
        df = pd.read_csv(SYMBOL_CSV_PATH)
        if 'Company Name' not in df.columns or 'Symbol' not in df.columns:
            print("Error: symbols.csv must have 'Company Name' and 'Symbol' columns.")
            raise ValueError("Invalid symbols.csv format")
    except Exception as e:
        print(f"Error reading symbols.csv: {e}")
        raise

    documents = []
    for _, row in df.iterrows():
        # Ensure data is string and clean
        company_name = str(row['Company Name']).strip()
        symbol = str(row['Symbol']).strip()
        
        if not company_name or not symbol:
            continue # Skip empty rows

        content = f"Company Name: {company_name}, Symbol: {symbol}"
        metadata = {
            "company_name": company_name,
            "symbol": symbol
        }
        documents.append(Document(page_content=content, metadata=metadata))
    
    if not documents:
        print(f"No valid data found in {SYMBOL_CSV_PATH}.")
        raise ValueError(f"No documents to process from {SYMBOL_CSV_PATH}")

    print("Creating symbol embeddings... (This may take a moment)")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(documents, embeddings)
    
    vector_store.save_local(SYMBOL_VECTOR_STORE_PATH)
    print(f"Symbol vector store saved to {SYMBOL_VECTOR_STORE_PATH}")

def get_symbol_retriever():
    """
    Loads the saved symbol FAISS vector store as a retriever.
    """
    if not os.path.exists(SYMBOL_VECTOR_STORE_PATH):
        print("Symbol vector store not found. Creating a new one...")
        create_symbol_vector_store()
        
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(SYMBOL_VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    # Returns top 3 matches as requested
    return vector_store.as_retriever(search_kwargs={"k": 3})