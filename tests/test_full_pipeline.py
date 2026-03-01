import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Ensure the script can find the 'src' directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.connection import SessionLocal
from src.database.models import CreditCard
from src.engine.excel_parser import parse_universal_bank_statement
from src.engine.transaction_tagger import tag_transactions_with_ai
from src.engine.calculator import (
    find_category_specialists, 
    calculate_overall_roi
)
from src.agent.chat_agent import get_financial_advice

def run_production_grade_test():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    print("\n" + "█"*60)
    print("🚀 STARTING FULL PRODUCTION PIPELINE TEST (TITANIUM ENGINE)")
    print("█"*60 + "\n")

    try:
        # --- STEP 1: DATA INGESTION ---
        print("📥 [1/5] Loading Transactions...")
        file_path = "data/sample_uploads/transactions (2).xlsx"
        raw_df = parse_universal_bank_statement(file_path)
        print("✅ Bank statement parsed successfully.")
        
        # --- STEP 2: AI TAGGING ---
        tagged_df = tag_transactions_with_ai(raw_df, api_key=api_key) 
        print("✅ Transactions tagged successfully.")

        # --- STEP 3: LIVE DB FETCH ---
        print("\n📡 [3/5] Fetching Live Card Data from Neon DB...")
        db = SessionLocal()
        db_cards = db.query(CreditCard).all()
        print(f"✅ Successfully fetched {len(db_cards)} cards from production.")
        
        # --- STEP 4: MATH ENGINE EXECUTION ---
        print("\n🧮 [4/5] Running Math Engine & ROI Analysis...")
        cat_winners = find_category_specialists(tagged_df, db_cards)
        roi_ranking = calculate_overall_roi(tagged_df, db_cards)
        
        # Calculating actual spend for the UI
        total_spend = float(tagged_df['amount'].sum())
        spending_map = tagged_df.groupby('category')['amount'].sum().to_dict()

        math_results = {
            "category_winners": cat_winners,
            "overall_roi_ranking": roi_ranking,
            "category_spending_map": spending_map, 
            "total_tracked_spend": total_spend      
        }
        print("✅ Mathematical optimization complete.")

        # --- STEP 5: GRAND DASHBOARD DISPLAY ---
        render_grand_dashboard(math_results)

        # --- STEP 6: INTERACTIVE AI ADVISOR ---
        launch_advisor_chat(math_results, db_cards, api_key)

    except Exception as e:
        print(f"\n❌ [CRITICAL PIPELINE FAILURE]: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()

def render_grand_dashboard(results):
    print("\n" + "★" * 80)
    print("🚀 YOUR PERSONALIZED WEALTH-MAXIMIZER DASHBOARD (TITANIUM EDITION)")
    print("★" * 80)

    # --------------------------------------------------
    # SECTION 1: CATEGORY-WISE IMPACT 
    # --------------------------------------------------
    print("\n🛒 [SECTION 1] CATEGORY-WISE OPTIMIZATION")
    print("-" * 50)
    
    cat_winners = results.get('category_winners', {})
    spending_map = results.get('category_spending_map', {})

    for cat, data in cat_winners.items():
        actual_spend = spending_map.get(cat, 0) 
        
        # STRICT KEY SYNC WITH CALCULATOR.PY ('winner' & 'savings')
        best_card = data.get('winner', 'Unknown Card')
        savings = data.get('savings', 0.0)
        
        print(f"🔹 Category: {cat}")
        
        if actual_spend > 0:
            effective_price = actual_spend - savings
            print(f"   - You spent ₹{actual_spend:,.2f} here.")
            print(f"   - If you had used the **{best_card}**, you would have saved **₹{savings:,.2f}**.")
            print(f"   - ✅ Result: You could have completed your {cat} purchases in only **₹{effective_price:,.2f}**!")
        else:
            print(f"   - Best Optimized Card: **{best_card}**")
            print(f"   - Potential Savings: **₹{savings:,.2f}**")
            
        print(f"   - 💡 Advisor Note: That's a direct reduction in your monthly expenses.\n")

    # --------------------------------------------------
    # SECTION 2: THE OVERALL PROFIT CHAMPIONS
    # --------------------------------------------------
    print("🏆 [SECTION 2] YOUR TOP 3 OVERALL PICKS")
    print("-" * 50)
    
    top_3_roi = results.get('overall_roi_ranking', [])[:3]
    total_spend = results.get('total_tracked_spend', 0)
    
    for i, card in enumerate(top_3_roi, 1):
        # STRICT KEY SYNC WITH CALCULATOR.PY ('net_roi')
        net_profit = card.get('net_roi', 0.0)
        card_name = card.get('card_name', 'Card')
        
        if i == 1:
            print(f"🥇 THE ABSOLUTE WINNER: **{card_name}**")
            print(f"   - Out of your total account debits of ₹{total_spend:,.2f} (which helped waive your annual fees!), this card maximized rewards on your eligible shopping.")
            print(f"   - It puts **₹{net_profit:,.2f}** back into your pocket after all fees.")
        else:
            print(f"🥈 Rank #{i}: **{card_name}**")
            print(f"   - A great backup card saving you ₹{net_profit:,.2f} overall.")

def launch_advisor_chat(math_results, db_cards, api_key):
    print("\n" + "="*70)
    print("💬 AI ADVISOR IS ONLINE (Ask me anything about the results above, card choices, etc...)")
    print("="*70)
    
    chat_history = []
    db_context = [
        {column.name: str(getattr(card, column.name)) for column in card.__table__.columns}
        for card in db_cards
    ]

    while True:
        user_input = input("\n🧑 You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
            
        print("⏳ Analyzing data...")
        response = get_financial_advice(user_input, math_results, db_context, chat_history, api_key)
        print(f"\n🤖 Advisor: {response}")
        
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    run_production_grade_test()