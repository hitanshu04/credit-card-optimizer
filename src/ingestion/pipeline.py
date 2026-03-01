import json
import os
import sys
import time

# 1. Path fixing so that one can find Python files
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ingestion.pdf_downloader import get_combined_text_from_urls
from src.ingestion.ai_extractor import extract_card_data
from src.database.connection import SessionLocal, init_db
from src.database.models import CreditCard

def save_card_to_db(structured_json_str, name):
    db = SessionLocal()
    try:
        if not structured_json_str:
            return

        data = json.loads(structured_json_str)
        
        # Mapping AI JSON keys to Table Columns
        fees = data.get("fees", {})
        rewards = data.get("rewards", {})
        perks = data.get("perks", {})
        benefits = data.get("other_benefits", {})

        existing_card = db.query(CreditCard).filter(CreditCard.card_name == name).first()
        
        card_values = {
            "card_name": name,
            "network": data.get("network"),
            "primary_category": data.get("primary_category"),
            "joining_fee": fees.get("joining"),
            "renewal_fee": fees.get("renewals"),
            "waiver_threshold": fees.get("waiver_spend"),
            "reward_type": rewards.get("reward_types"),
            "reward_rate": rewards.get("reward_rates"),
            "reward_multiplier": rewards.get("multipliers"),
            "inr_value_per_unit": rewards.get("unified_inr_value"),
            "reward_expiry": rewards.get("expiry"),
            "earning_caps": rewards.get("earning_caps"),
            "redemption_options": rewards.get("redemption_options"),
            "lounge_domestic": perks.get("lounges_domestic"),
            "lounge_international": perks.get("lounges_international"),
            "movie_benefits": perks.get("movies"),
            "golf_benefits": perks.get("golf"),
            "other_perks": perks.get("others"),
            "welcome_benefits": benefits.get("welcome_benefits"),
            "milestone_benefits": benefits.get("milestones"),
            "special_tie_ups": benefits.get("special_tie_ups")
        }
        # 2. HYBRID MERGE LOGIC
        # Path to manual math data file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        manual_data_path = os.path.join(base_dir, 'data', 'manual_math_data.json')

        if os.path.exists(manual_data_path):
            try:
                with open(manual_data_path, 'r') as f:
                    manual_data = json.load(f)
                
                # If current card is in manual JSON, then overwrite values.
                if name in manual_data:
                    print(f"      -> 🔄 [HYBRID MERGE] Injecting accurate math config for: {name}")
                    math_rules = manual_data[name]
                    for key, val in math_rules.items():
                        if val is not None:
                            card_values[key] = val
            except Exception as e:
                print(f"      -> ❌ [HYBRID ERROR] Could not read manual data: {e}")
        # # 2. 🔥 HYBRID MERGE LOGIC (The 20 LPA Move) 🔥
        # Path to your manual math data file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        manual_data_path = os.path.join(base_dir, 'data', 'manual_math_data.json')

        if os.path.exists(manual_data_path):
            try:
                with open(manual_data_path, 'r') as f:
                    manual_data = json.load(f)
                
                # Agar current card manual JSON mein hai, toh values overwrite/fill kar do
                if name in manual_data:
                    print(f"      -> 🔄 [HYBRID MERGE] Injecting accurate math config for: {name}")
                    math_rules = manual_data[name]
                    for key, val in math_rules.items():
                        if val is not None:
                            card_values[key] = val
            except Exception as e:
                print(f"      -> ❌ [HYBRID ERROR] Could not read manual data: {e}")
        
        # 3. Final Database Upsert (The Smart Update)
        if existing_card:
            print(f"      -> Updating existing card: {name}")
            for key, value in card_values.items():
                if value is not None:
                    setattr(existing_card, key, value)
        else:
            print(f"      -> Creating fully normalized record for: {name}")
            new_card = CreditCard(**card_values)
            db.add(new_card)
        
        db.commit()
        print(f"      -> [DB SUCCESS] {name} saved with 15+ normalized columns!")
        
    except Exception as e:
        print(f"      -> [DB ERROR] Saving failed: {e}")
        db.rollback()
    finally:
        db.close()

def run_ingestion_pipeline():
    print("\n🚀 Running Final Ingestion Pipeline...")
    
    # Tables check (Safety first)
    init_db()

    # Read Sources 
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(base_dir, 'config', 'sources.json')
    
    try:
        with open(config_path, 'r') as f:
            cards = json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found at {config_path}")
        return

    for card in cards:
        name = card.get("card_name")
        urls = card.get("urls") 

        print(f"\n[+] Processing: {name}")

        # Step A: Check if URLs exist
        if not urls:
            print(f"      -> [SKIP] No URLs found for {name}")
            continue
            
        # Step B: Aggregate text from both Landing Page and PDF
        raw_text = get_combined_text_from_urls(urls)
        
        if raw_text:
            
            structured_json = extract_card_data(raw_text, name)
            
            # Step C: Save to PostgreSQL only if AI provided data
            if structured_json:
                save_card_to_db(structured_json, name)
            
            # Wait for 10 seconds to respect Free Tier rate limits
            print("      -> Sleeping for 10 seconds (Rate Limit Cooldown)...")
            time.sleep(10)
        else:
            print(f"      -> [SKIP] Could not extract any text for {name}")

if __name__ == "__main__":
    run_ingestion_pipeline()