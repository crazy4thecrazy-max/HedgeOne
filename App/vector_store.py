import os
import sys
import pandas as pd
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from config import (
    EQUITY_CSV_FILE, EQUITY_FAISS_INDEX, 
    FNO_CSV_FILE, FNO_FAISS_INDEX, EMBEDDINGS_MODEL
)

def create_vector_store_if_missing(csv_path: str, index_path: str, embeddings_model):
    """Creates and saves a FAISS vector store if it doesn't already exist."""
    if os.path.exists(index_path):
        print(f"Vector store '{index_path}' already exists. Loading...")
        sys.stdout.flush()
        return
    
    print(f"Vector store '{index_path}' not found. Creating from '{csv_path}'...")
    sys.stdout.flush()
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at '{csv_path}'. Cannot create vector store.")
        sys.stdout.flush()
        exit()
        
    try:
        df = pd.read_csv(csv_path)
        documents = []

        # --- THIS IS THE UPDATED LOGIC ---
        if csv_path == FNO_CSV_FILE:
            # For F&O file, we expect 'Company name', 'Symbol', and 'Lot size'
            if 'Company name' not in df.columns or 'Symbol' not in df.columns or 'Lot size' not in df.columns:
                print(f"Error: F&O CSV '{csv_path}' must contain 'Company name', 'Symbol', and 'Lot size' columns.")
                sys.stdout.flush()
                exit()
                
            documents = [
                Document(page_content=f"{row['Company name']},{row['Symbol']},{row['Lot size']}")
                for _, row in df.iterrows()
            ]
            print(f"Loaded F&O data with Lot Size.")
            sys.stdout.flush()
            
        else:
            # For all other files (like equity), just use 'Company name' and 'Symbol'
            if 'Company name' not in df.columns or 'Symbol' not in df.columns:
                print(f"Error: CSV '{csv_path}' must contain 'Company name' and 'Symbol' columns.")
                sys.stdout.flush()
                exit()
                
            documents = [
                Document(page_content=f"{row['Company name']},{row['Symbol']}")
                for _, row in df.iterrows()
            ]
        # --- END OF UPDATED LOGIC ---

        if not documents:
            print(f"Error: No documents created from '{csv_path}'. Is the file empty?")
            sys.stdout.flush()
            exit()
            
        vectorstore = FAISS.from_documents(documents, embeddings_model)
        vectorstore.save_local(index_path)
        print(f"Successfully created and saved vector store at '{index_path}'.")
        sys.stdout.flush()
        
    except Exception as e:
        print(f"Error creating vector store from '{csv_path}': {e}")
        sys.stdout.flush()
        exit()

# --- Initialize and Load Stores ---
try:
    embeddings_model = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)
    
    # --- Create/Load Equity Vector Store ---
    create_vector_store_if_missing(EQUITY_CSV_FILE, EQUITY_FAISS_INDEX, embeddings_model)
    equity_vectorstore = FAISS.load_local(EQUITY_FAISS_INDEX, embeddings_model, allow_dangerous_deserialization=True)
    print("Equity symbol vector store loaded!")
    sys.stdout.flush()

    # --- Create/Load F&O Vector Store ---
    create_vector_store_if_missing(FNO_CSV_FILE, FNO_FAISS_INDEX, embeddings_model)
    fno_vectorstore = FAISS.load_local(FNO_FAISS_INDEX, embeddings_model, allow_dangerous_deserialization=True)
    print("F&O symbol vector store loaded!")
    sys.stdout.flush()

except Exception as e:
    print(f"Error loading vector stores: {e}")
    sys.stdout.flush()
    exit()