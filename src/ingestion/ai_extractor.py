import os
import json
# from groq import Groq
from google import genai
from google.genai import types

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 1. Load .env file.
load_dotenv()

# 2. Configuration
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

# 3. Initialize GenAI Client
client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash" 


# if not API_KEY:
#     raise ValueError("GROQ_API_KEY not found in .env file!")

# # 3. INITIALIZE THE NEW SDK CLIENT
# # New 'google-genai' package.
# client = Groq(api_key=API_KEY)

# 4. THE STRICT BLUEPRINT (SCHEMA)
# Each class represents a category so that code is clean.

class Fees(BaseModel):
    joining: str | None = Field(description="Exact Joining fee amount")
    renewals: str | None = Field(description="Exact Annual or Renewal fee amount")
    waiver_spend: str | None = Field(description="The spend threshold and specific timeframe required to waive off any fees (e.g., 20k in 90 days or 1 Lakh in a year).")

class Rewards(BaseModel):
    reward_types: str | None = Field(description="Points, miles, coins, or cashback")
    reward_rates: str | None = Field(description="Base reward rates (e.g., 1 point per 100 Rs spent)")
    multipliers: str | None = Field(description="MUST explicitly list EVERY single merchant name (e.g., Amazon, Swiggy, Zomato) and exact %. DO NOT SUMMARIZE.")
    
    earning_caps: str | None = Field(description="Extract the exact maximum points earned per month. YOU MUST INCLUDE WHERE IT APPLIES (e.g., '1000 points on 10 online merchants', '1000 points on other spends'). DO NOT SUMMARIZE.")
    
    unified_inr_value: str | None = Field(description="The value of 1 point/mile in Indian Rupees (INR)")
    
    redemption_options: str | None = Field(description="CRITICAL: You MUST extract EVERY SINGLE mathematical limit and rule. Include: minimum points needed (e.g., 500 points), exact INR values for different portals (e.g., SmartBuy 1 RP = 0.30 Rs), maximum % of booking value allowed (e.g., 50% or 70%), and monthly redemption caps (e.g., 3000 or 50000 points). DO NOT SUMMARIZE. Write every rule with its numbers.")
    
    expiry: str | None = Field(description="Validity period or expiry of the reward points")

class Perks(BaseModel):
    lounges_domestic: str | None = Field(description="Domestic airport lounge access details")
    lounges_international: str | None = Field(description="International airport lounge access details")
    movies: str | None = Field(description="Movie ticket offers and discounts and Exact movie platform names like BookMyShow, PVR, or null. DO NOT SUMMARIZE.")
    golf: str | None = Field(description="Golf course access or coaching benefits")
    others: str | None = Field(description="Any other perks not covered above")

class OtherBenefits(BaseModel):
    welcome_benefits: str | None = Field(description="Benefits given at the time of joining/card activation")
    milestones: str | None = Field(description="Benefits triggered after reaching a spend milestone")
    special_tie_ups: str | None = Field(description="List specific brand names like Taj, Marriott, Swiggy Dineout. DO NOT SUMMARIZE.")

# MAIN SCHEMA: Combines all categories at a place.
class CreditCardSchema(BaseModel):
    card_name: str
    network: str | None = Field(description="Card network: Visa, Mastercard, Rupay, etc.")
    primary_category: str | None = Field(description="Main category: Cashback, rewards, dining, fuel, etc.")
    fees: Fees
    rewards: Rewards
    perks: Perks
    other_benefits: OtherBenefits

# 5. THE EXTRACTION FUNCTION
def extract_card_data(raw_text: str, card_name: str) -> str:
    print(f"      -> Using Model: {MODEL_NAME} for extraction...")
    
    # We convert the Pydantic model to a JSON Schema string to 'teach' the AI
    schema_instructions = json.dumps(CreditCardSchema.model_json_schema(), indent=2)

    prompt = f"""
    You are a meticulous Senior Financial Data Auditor. Your task is to extract data for the '{card_name}' credit card.
    
    INSTRUCTIONS:
    1. Scan the text for: Network, Fees, Rewards, Perks, and Other Benefits.
    2. Adhere strictly to this JSON SCHEMA:
    {schema_instructions}

    CRITICAL RULES (DO NOT IGNORE):
    - ZERO SUMMARIZATION: Never summarize or group items. If the text lists specific merchants (e.g., Amazon, Swiggy, BookMyShow, Zomato, Taj, Swiggy Dineout), you MUST extract and write EVERY SINGLE NAME explicitly.
    - REWARD MULTIPLIERS: Map exact percentages to exact merchant names. Example format: "5% on Amazon, BookMyShow, Swiggy. 1% on Base Spends."
    - NO HALLUCINATION: If a specific feature is not found in the text, you MUST return 'null'. Do not guess or make up numbers.
    - Output MUST be a clean JSON object. No intro or outro text.
    """

    try:# Gemini native JSON response format
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, f"RAW TEXT FROM PDF & WEBPAGE:\n{raw_text}"],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        return response.text
    except Exception as e:
        print(f"      -> [GEMINI ERROR] Extraction failed: {e}")
        return ""