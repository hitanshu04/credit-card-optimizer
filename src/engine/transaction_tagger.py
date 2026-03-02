import json
import time
import pandas as pd  
from google import genai
from google.genai import types

CATEGORIES = [
    "E-Commerce", "Food Delivery", "Entertainment", "Travel & Transit", 
    "Health & Groceries", "Bills & Utilities", "Offline Spend", "P2P/Ignored"
]

def tag_transactions_with_ai(df, api_key):
    """
    Uses strict ID-based mapping to guarantee ZERO alteration of original financial amounts.
    """
    # 1. EMPTY DATA CHECK: Return exact original schema safely
    if df.empty:
        return pd.DataFrame(columns=['txn_date', 'txn_note', 'amount', 'category', 'merchant'])

    client = genai.Client(api_key=api_key)
    
    # 2. CREATE A SAFE COPY AND ASSIGN UNIQUE IDs
    # Don't rename 'txn_note' in the dataframe. The database schema stays safe.
    working_df = df.copy()
    
    # Python generates 100% deterministic IDs. 
    working_df['txn_id'] = ['txn_' + str(i) for i in range(len(working_df))]
    
    # Set the Doomsday Fallback as default. 
    # If AI completely fails, no fake math happens. It defaults to 0% reward logic.
    working_df['category'] = 'P2P/Ignored' 
    working_df['merchant'] = 'Unknown'

    # Convert to list of dictionaries for batch processing
    transactions = working_df.to_dict('records')
    batch_size = 50
    
    print("\n🏷️ [2/5] Tagging Transactions via AI (Strict ID-Mapping Mode)...")

    # 3. BATCH PROCESSING
    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i+batch_size]
        
        # Hide 'amount' and 'txn_date' from AI completely!
        # Only send the ID and the text note.
        ai_payload = [{"id": row['txn_id'], "note": row['txn_note']} for row in batch]
        
        # THE STRICT LEGAL PROMPT
        prompt = f"""
        Assign ONE category to each transaction strictly from this exact list: {CATEGORIES}.
        If it's a personal UPI transfer (e.g., to a person's name), use 'P2P/Ignored'.
        
        CRITICAL RULES:
        1. You MUST return the EXACT SAME 'id' that was passed in the input data. Do not copy or make up IDs.
        2. Return ONLY a valid JSON array.
        3. If it is a personal UPI transfer (to a person's name), a 'Self Transfer', a loan EMI, or a Credit Card Bill Payment, you MUST strictly use 'P2P/Ignored'. These are non-rewardable.
        
        Format your response EXACTLY like this:
        [{{"id": "<exact_id_from_input>", "category": "<your_category>", "merchant": "<merchant_name>"}}]
        
        Data to process: {ai_payload}
        """

        max_retries = 3
        retries = 0
        success = False

        # 4. THE STRICT RETRY LOOP
        while retries < max_retries and not success:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0,
                        top_p=0.1
                    )
                )
                
                results = json.loads(response.text)
                
                # Length Check Firewall: Did AI skip any transaction?
                if len(results) != len(batch):
                    raise ValueError(f"Length mismatch! Sent {len(batch)}, AI returned {len(results)}")
                
                # 5. THE IMP MERGE (ID-BASED ANCHORING)
                for ai_res in results:
                    t_id = ai_res.get('id')
                    ai_cat = ai_res.get('category', 'P2P/Ignored')
                    ai_merch = ai_res.get('merchant', 'Unknown')
                    
                    # Strict Vocabulary Rule: If AI hallucinates a category, kill it.
                    if ai_cat not in CATEGORIES:
                        ai_cat = 'P2P/Ignored' 
                        
                    # Find the exact row using the ID and safely paste ONLY the category and merchant.
                    # The original 'amount' and 'txn_date' are completely untouched.
                    idx_mask = working_df['txn_id'] == t_id
                    if idx_mask.any():
                        working_df.loc[idx_mask, 'category'] = ai_cat
                        working_df.loc[idx_mask, 'merchant'] = ai_merch
                
                success = True 
                print(f"  ✅ Batch {i//batch_size + 1} tagged accurately (Amounts & Schema 100% untouched).")
                
            except Exception as e:
                retries += 1
                print(f"  ⏳ Error in Batch {i//batch_size + 1} ({str(e)}). Retrying ({retries}/{max_retries})...")
                time.sleep(35) # Let the API cool down before trying again
        
        # 6. GRACEFUL DEGRADATION (DOOMSDAY FALLBACK)
        if not success:
            print(f"  ⚠️ Warning: AI completely failed for Batch {i//batch_size + 1}. Applied safe 'P2P/Ignored' fallback to protect financial logic.")

        # Safe gap between successful batches to respect Free-Tier API Limits
        time.sleep(25)

    # 7. CLEANUP: Remove the temporary ID column before passing to Layer 3
    working_df = working_df.drop(columns=['txn_id'])
    
    return working_df