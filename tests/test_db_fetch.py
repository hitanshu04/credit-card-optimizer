import os
import sys

# Path fixing so that src imports work properly
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import original files
from src.database.connection import SessionLocal
from src.database.models import CreditCard

def test_neon_db_connection():
    print("\n" + "★"*50)
    print("🔌 TESTING NEON DB CONNECTION (LIVE PRODUCTION)")
    print("★"*50 + "\n")
    
    # 1. Open the DB Session securely
    db = SessionLocal()
    
    try:
        print("⏳ Fetching data from Neon DB. Please wait...")
        
        # 2. Safely query all credit cards
        cards = db.query(CreditCard).all()
        
        if not cards:
            print("\n⚠️ Database is connected, but no cards were found! (Table might be empty)")
            return
            
        print(f"\n✅ SUCCESS! Found {len(cards)} credit cards in the database.\n")
        
        # 3. Print a quick snapshot to verify data quality
        print("💳 --- SAMPLE DATA FETCHED (Top 3 Cards) ---")
        for i, card in enumerate(cards[:3], 1):
            print(f" {i}. Card Name: {card.card_name}")
            print(f"    - Network:  {card.network}")
            print(f"    - Category: {card.primary_category}")
            print(f"    - Fee:      ₹{card.joining_fee}")
            print(f"    - Base Rate:{card.reward_rate}")
            print("-" * 40)
            
        print("\n🚀 Backend is 1000% ready for the Streamlit UI!")
        
    except Exception as e:
        print(f"\n❌ [CRITICAL ERROR]: Failed to connect or fetch data.\nDetails: {str(e)}")
        print("\n💡 Tip: Check if your .env file has the correct DATABASE_URL.")
    
    finally:
        # 4. Close the connection to prevent memory leaks (Best Practice)
        db.close()

if __name__ == "__main__":
    test_neon_db_connection()