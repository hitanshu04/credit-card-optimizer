import os
import json
import sys
from dotenv import load_dotenv

# Path fixing so that imports from src work
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agent.chat_agent import get_financial_advice

def run_chat_test():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file.")
        return

    # 1. THE MOCK DB 
    db_context = [
        {
            "card_name": "SBI Cashback", "primary_category": "Shopping", "joining_fee": 999.0,
            "waiver_threshold": 200000.0, "reward_rate": 1.0, "multipliers": {"amazon": 5.0},
            "inr_value_per_unit": 1.0, "lounge_domestic": "0", "lounge_intl": "0", 
            "movie_benefits": "None", "golf_benefits": "None", "special_tieups": "None"
        },
        {
            "card_name": "Axis Atlas", "primary_category": "Travel", "joining_fee": 5000.0,
            "waiver_threshold": 500000.0, "reward_rate": 2.0, "multipliers": {"makemytrip": 5.0},
            "inr_value_per_unit": 1.0, "lounge_domestic": "4", "lounge_intl": "2", 
            "movie_benefits": "None", "golf_benefits": "None", "special_tieups": "None"
        }
    ]

    # 2. THE EXACT MATH OUTPUT FROM LAYER3-VERIFIED & TESTED
    math_context = {
        "category_winners": {
            'Offline Spend': {'winner': 'Axis Atlas', 'savings': 502.2},
            'E-Commerce': {'winner': 'Axis Atlas', 'savings': 301.46},
            'Bills & Utilities': {'winner': 'Axis Atlas', 'savings': 1929.43}
        },
        "overall_roi_ranking": [
            {'card_name': 'Axis Atlas', 'net_roi': 3073.09, 'waiver_status': 'Applied', 'total_spend': 165216.35},
            {'card_name': 'SBI Cashback', 'net_roi': 1536.54, 'waiver_status': 'Applied', 'total_spend': 165216.35}
        ],
        "lifestyle_perks": [
            {'card_name': 'SBI Cashback', 'top_categories': ['Bills & Utilities', 'Offline Spend', 'E-Commerce'], 'perks_highlight': ['Shopping: Best for online e-commerce.']}
        ]
    }

    # 3. TERMINAL CHAT INTERFACE
    chat_history = []
    
    print("\n" + "="*60)
    print("🤖 AI Financial Advisor Terminal (Type 'exit' to quit)")
    print("="*60 + "\n")
    print("Agent is ready! It knows you saved ₹3073 with Axis Atlas.\n")
    
    
    print("📊 --- THE 'CHEAT SHEET' GIVEN TO AI ---")
    print(json.dumps(math_context, indent=2))
    print("----------------------------------------\n")

    # === SIMULATING THE STREAMLIT UI DISPLAY BEFORE CHAT ===
    print("\n" + "★"*60)
    print(" 🚀 YOUR PERSONALIZED CREDIT CARD DASHBOARD")
    print("★"*60)
    
    print("\n🏆 OVERALL ROI CHAMPIONS:")
    for i, card in enumerate(math_context["overall_roi_ranking"][:3], 1): # Top 3 only
        print(f"  {i}. {card['card_name']} | Net Savings: ₹{card['net_roi']} | Fee: {card['waiver_status']}")
        
    print("\n🛒 CATEGORY SPECIALISTS:")
    for cat, data in math_context["category_winners"].items():
        if data['savings'] > 0:
            print(f"  - {cat}: {data['winner']} (Saved ₹{data['savings']})")
            
    print("\n✨ YOUR LIFESTYLE DNA:")
    for perk in math_context["lifestyle_perks"]:
        print(f"  - {perk['card_name']} match: {perk['perks_highlight'][0]}")
    
    print("\n" + "="*60)
    print("💬 ADVISOR CHAT (Ask me why these cards won, details, or comparisons!)")
    print("="*60 + "\n")

    while True:
        user_msg = input("🧑 You: ")
        
        if user_msg.lower() in ['exit', 'quit']:
            print("👋 Exiting chat...")
            break
            
        print("⏳ Thinking...")
        
        # Calling Layer 4
        response = get_financial_advice(
            user_message=user_msg,
            math_context=math_context,
            db_context=db_context,
            chat_history=chat_history,
            api_key=api_key
        )
        
        print(f"\n🤖 Advisor: {response}\n")
        print("-" * 60)
        
        # Storing memory
        chat_history.append({"role": "user", "content": user_msg})
        chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    run_chat_test()