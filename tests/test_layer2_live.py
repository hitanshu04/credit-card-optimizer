import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Path fixing so that imports from src work
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.engine.excel_parser import parse_universal_bank_statement
from src.engine.transaction_tagger import tag_transactions_with_ai

def test_layer2_flow(file_path):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    print("\n--- Phase 1: Cleaning Raw Excel ---")
    # 1. Test Excel Parser 
    df_clean = parse_universal_bank_statement(file_path)
    print(f"✅ Cleaned! Found {len(df_clean)} Debit Transactions.")
    print(df_clean.head()) # See first 5 records

    print("\n--- Phase 2: AI Categorization (Layer 2 Magic) ---")
    # 2. AI Tagger Test (Send 20 records for testing)
    df_sample = df_clean.head(20) 
    
    df_tagged = tag_transactions_with_ai(df_sample, api_key)
    
    print("\nFINAL LAYER 2 OUTPUT")
    print(df_tagged[['note', 'amount', 'category', 'merchant']])

if __name__ == "__main__":
    # File Path
    FILE_PATH = "data/sample_uploads/transactions (2).xlsx"
    test_layer2_flow(FILE_PATH)