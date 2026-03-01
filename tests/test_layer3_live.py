import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Path fixing so that imports from src work
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 1. Importing Layer 2 Functions
from src.engine.excel_parser import parse_universal_bank_statement
from src.engine.transaction_tagger import tag_transactions_with_ai

# 2. Importing Layer 3 Functions 
from src.engine.calculator import find_category_specialists, calculate_overall_roi, analyze_lifestyle_match

def test_layer3_flow(file_path):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    print("\n--- Phase 1: Cleaning Raw Excel ---")
    df_clean = parse_universal_bank_statement(file_path)
    print(f"✅ Cleaned! Found {len(df_clean)} Debit Transactions.")
    print(df_clean.head()) # See first 5 records

    print("\n--- Phase 2: AI Categorization (Layer 2) ---")
    df_sample = df_clean.head(20) # 20 records for testing 
    df_tagged = tag_transactions_with_ai(df_sample, api_key)
    print("✅ Tagging Complete!")
    print(df_tagged[['note', 'amount', 'category', 'merchant']])

    # ---------------------------------------------------------
    # LAYER 2 TO LAYER 3 BRIDGE
    # Rename columns so Layer 3 understands them perfectly
    # ---------------------------------------------------------
    df_tagged = df_tagged.rename(columns={
        'amount': 'Amount', 
        'category': 'Category', 
        'merchant': 'Merchant'
    })

    print("\n--- Phase 3: Running Math Engine (Layer 3) ---")
    
    # DUMMY NEON DB (Coz DB isn't connected yet)
    mock_db = [
        {
            "card_name": "SBI Cashback", "primary_category": "Shopping", "joining_fee": 999.0, 
            "waiver_threshold": 200000.0, "reward_rate": 1.0, "multipliers": '{"amazon": 5.0}', 
            "earning_caps": '{"monthly_total": 5000}', "inr_val_per_unit": 1.0, 
            "lounge_domestic": "0", "lounge_intl": "0", "movie_benefits": "None", 
            "golf_benefits": "None", "special_tieups": "None"
        },
        {
            "card_name": "Axis Atlas", "primary_category": "Travel", "joining_fee": 5000.0, 
            "waiver_threshold": 500000.0, "reward_rate": 2.0, "multipliers": '{"makemytrip": 5.0}', 
            "earning_caps": '{"monthly_total": 10000}', "inr_val_per_unit": 1.0, 
            "lounge_domestic": "4", "lounge_intl": "2", "movie_benefits": "None", 
            "golf_benefits": "None", "special_tieups": "None"
        }
    ]
    # Python's SimpleNamespace dictionary converted to Object.
    from types import SimpleNamespace
    mock_db_objects = [SimpleNamespace(**card) for card in mock_db]

    # Run Module 1: Category
    print("\n🏆 1. CATEGORY SPECIALISTS:")
    cat_winners = find_category_specialists(df_tagged, mock_db_objects)
    print(cat_winners)

    # Run Module 2: Overall ROI
    print("\n💰 2. OVERALL ROI CHAMPION:")
    roi_champion = calculate_overall_roi(df_tagged, mock_db_objects)
    print(roi_champion)

    # Run Module 3: Lifestyle
    print("\n✨ 3. LIFESTYLE MATCH:")
    lifestyle = analyze_lifestyle_match(df_tagged, mock_db_objects)
    print(lifestyle)

if __name__ == "__main__":
    # File Path
    FILE_PATH = "data/sample_uploads/transactions (2).xlsx"
    test_layer3_flow(FILE_PATH)