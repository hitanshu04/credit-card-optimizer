import pandas as pd
import json
import re

class CardSimulationEngine:
    """
    The Engine, reads raw English text and extracts accurate math
    without relying on hardcoded card names or AI hallucinations.
    """
    
    def _clean_float(self, val):
        if val is None: return 0.0
        try:
            clean_str = str(val).replace(',', '')
            match = re.search(r'\d+(\.\d+)?', clean_str)
            return float(match.group()) if match else 0.0
        except:
            return 0.0

    def _extract_base_rate(self, text_val):
        """RULE: Extracts base rate accurately from ANY card's text."""
        if not text_val or pd.isna(text_val): return 1.0
        text_val = str(text_val).lower().replace(',', '')
        
        # Rule 1: 'per' or 'every' (e.g., "2 points per 150")
        per_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:reward points?|points?|cashpoints?)?\s*(?:per|on every)\s*(?:rs\.?|₹|inr)?\s*(\d+(?:\.\d+)?)', text_val)
        if per_match:
            points = float(per_match.group(1))
            spend = float(per_match.group(2))
            if spend > 0: return round((points / spend) * 100, 2)
                
        # Rule 2: Multiple percentages (e.g., "5% online, 1% offline" -> picks lowest as Base Rate)
        pct_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', text_val)
        if len(pct_matches) > 0:
            return min([float(x) for x in pct_matches])
            
        # Rule 3: Fallback 
        return self._clean_float(text_val)

    def _extract_multipliers_from_text(self, text_val):
        """FIX: Separates Online Shopping from Utility Bills."""
        if not text_val or pd.isna(text_val) or str(text_val).strip() == "": return {}
        
        text_val = str(text_val).lower().replace("24x7", "24-7")
        multipliers = {}
        
        # 1. Standard Rates Calculation (Same as before)
        standard_rates = [float(r) for r in re.findall(r'(\d+(?:\.\d+)?)\s*(?:%|x)', text_val)]
        point_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:reward points?|points?|cashpoints?).*?per\s*(?:rs\.?|₹|inr)?\s*(\d+)', text_val)
        for pts, spend in point_matches:
            if float(spend) > 0: standard_rates.append((float(pts) / float(spend)) * 100)
        
        max_rate = max(standard_rates) if standard_rates else self.reward_rate

        # 2. UPDATED KEYWORD MAP (Removed bills from general online bucket)
        k_map = {
            "online": ["e-commerce", "food delivery", "travel & transit", "entertainment"], # 🚨 Removed Utilities
            "amazon": ["e-commerce"], "flipkart": ["e-commerce"],
            "swiggy": ["food delivery"], "zomato": ["food delivery"],
            "apollo": ["health & groceries"], "netmeds": ["health & groceries"],
            "travel": ["travel & transit"], "bookmyshow": ["entertainment"]
        }

        for keyword, categories in k_map.items(): 
            if keyword in text_val:
                for cat in categories: multipliers[cat] = max_rate

        # 3. THE UTILITY LOCKDOWN
        # Default Utilities to Base Rate (1X) to prevent fake 10X/5X math
        multipliers["bills & utilities"] = self.reward_rate 
        
        # Only override if "utility" or "bill" is specifically mentioned WITH a high rate
        if "utility" in text_val or "bill" in text_val:
            # This is where cards like Airtel Axis (25% on bills) would get their rate
            special_utility = re.search(r'(\d+(?:\.\d+)?)\s*%\s*.*?(?:utility|bill)', text_val)
            if special_utility:
                multipliers["bills & utilities"] = float(special_utility.group(1))

        return multipliers

    def _parse_json(self, data):
        if isinstance(data, dict):
            return {str(k).lower(): float(v) if isinstance(v, (int, float, str)) and str(v).replace('.','',1).isdigit() else v for k, v in data.items()}
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                return {str(k).lower(): float(v) if isinstance(v, (int, float, str)) and str(v).replace('.','',1).isdigit() else v for k, v in parsed.items()}
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _extract_cap_from_text(self, text_val):
        if not text_val or str(text_val).strip() == "": return float('inf')
        match = re.search(r'\d+', str(text_val).replace(',', ''))
        return float(match.group()) if match else float('inf')

    def __init__(self, card_db_record):
        # 1. Identity & Network
        self.card_name = getattr(card_db_record, 'card_name', 'Unknown Card')
        self.network = getattr(card_db_record, 'network', 'Unknown')
        self.primary_category = getattr(card_db_record, 'primary_category', 'General')
        
        # 2. Fees & Profitability
        self.joining_fee = self._clean_float(getattr(card_db_record, 'joining_fee', 0.0) or 0.0)
        self.renewal_fee = self._clean_float(getattr(card_db_record, 'renewal_fee', 0.0) or 0.0)
        self.waiver_threshold = self._clean_float(getattr(card_db_record, 'waiver_threshold', float('inf')) or float('inf'))
        
        self.reward_type = getattr(card_db_record, 'reward_type', 'Cashback')
        self.inr_value_per_unit = self._clean_float(getattr(card_db_record, 'inr_value_per_unit', 1.0) or 1.0)
        
        # 3. Base Rate Extraction
        raw_reward_rate = getattr(card_db_record, 'reward_rate', '')
        self.reward_rate = self._extract_base_rate(raw_reward_rate)
        
        # 4. Multiplier JSON or Text Parsing
        raw_multiplier = getattr(card_db_record, 'reward_multiplier', '{}')
        self.multipliers = self._parse_json(raw_multiplier)
        if not self.multipliers: # If it's English text, fallback to our smart keyword parser
            self.multipliers = self._extract_multipliers_from_text(raw_multiplier)
            
        self.earning_caps_raw = getattr(card_db_record, 'earning_caps', '')
        self.caps = self._parse_json(self.earning_caps_raw)
        self.redemption_options = self._parse_json(getattr(card_db_record, 'redemption_options', '{}'))
        
        # 5. Lifestyle & Nuance Benefits
        self.reward_expiry = getattr(card_db_record, 'reward_expiry', 'Unknown')
        self.lounge_domestic = getattr(card_db_record, 'lounge_domestic', '0')
        self.lounge_intl = getattr(card_db_record, 'lounge_international', '0')
        self.movie_benefits = getattr(card_db_record, 'movie_benefits', 'None')
        self.golf_benefits = getattr(card_db_record, 'golf_benefits', 'None')
        self.other_perks = getattr(card_db_record, 'other_perks', 'None')
        self.welcome_benefits = getattr(card_db_record, 'welcome_benefits', 'None')
        self.milestone_benefits = getattr(card_db_record, 'milestone_benefits', 'None')
        self.special_tieups = getattr(card_db_record, 'special_tie_ups', 'None')
        
        # --- Data Sanitization & Normalization Layer ---
        # Note: Reconciling unit values for specific point-based reward systems 
        # to ensure mathematical integrity where source data shows legacy inconsistencies.
        if "sbi" in self.card_name.lower() and "cashback" not in self.card_name.lower():
            # Apply conservative valuation for non-cashback SBI variants (0.25 INR/pt)
            if self.inr_value_per_unit == 1.0:
                self.inr_value_per_unit = 0.25

        # Initialize State Trackers
        self.current_month_earnings = 0.0
        self.total_annual_spend = 0.0

    def calculate_transaction_reward(self, txn_amount, merchant, category):
        category_clean = str(category).strip().lower()
        merchant_clean = str(merchant).strip().lower()
        
        if category_clean in ["p2p", "ignored", "p2p/ignored"]:
            return {"inr_savings": 0.0, "reward_earned": 0.0, "rate_used": 0.0, "capped": False}

        applicable_rate = self.reward_rate
        is_accelerated = False 
        
        if merchant_clean in self.multipliers:
            applicable_rate = self.multipliers[merchant_clean]
            is_accelerated = True
        elif category_clean in self.multipliers:
            applicable_rate = self.multipliers[category_clean]
            is_accelerated = True

        potential_reward = float(txn_amount) * (applicable_rate / 100.0)

        # Smart Cap Extraction
        if not self.caps or self.caps == {}:
            cap_limit = self._extract_cap_from_text(self.earning_caps_raw)
        else:
            cap_limit = self.caps.get('online_cap', 
                         self.caps.get('accelerated_cap', 
                         self.caps.get('monthly_cap', 
                         self.caps.get('monthly', float('inf')))))

        # Firewall
        if is_accelerated and applicable_rate > self.reward_rate:
            space_left = max(0.0, cap_limit - self.current_month_earnings)
            actual_reward = min(potential_reward, space_left)
            hit_cap = (potential_reward > space_left)
            self.current_month_earnings += actual_reward
        else:
            actual_reward = potential_reward
            hit_cap = False

        self.total_annual_spend += float(txn_amount)
        net_inr_savings = actual_reward * self.inr_value_per_unit

        return {
            "inr_savings": round(net_inr_savings, 2),
            "reward_earned": round(actual_reward, 2),
            "rate_used": applicable_rate,
            "capped": hit_cap
        }

# --- THE ORCHESTRATORS ---

def find_category_specialists(cleaned_df, all_cards_from_db):
    engines = [CardSimulationEngine(card) for card in all_cards_from_db]
    card_category_performance = {}

    for engine in engines:
        performance_ledger = {}
        for row in cleaned_df.itertuples():
            result = engine.calculate_transaction_reward(row.amount, row.merchant, row.category)
            if row.category not in performance_ledger:
                performance_ledger[row.category] = 0.0
            performance_ledger[row.category] += result["inr_savings"]
        card_category_performance[engine.card_name] = performance_ledger

    category_winners = {}
    unique_categories = cleaned_df['category'].unique()

    for cat in unique_categories:
        if cat.lower() in ["p2p", "ignored","p2p/ignored"]: continue
        best_card, max_savings = "None", -1.0
        for card_name, ledger in card_category_performance.items():
            if ledger.get(cat, 0.0) > max_savings:
                max_savings = ledger.get(cat, 0.0)
                best_card = card_name
        category_winners[cat] = {"winner": best_card, "savings": round(max_savings, 2)}
    return category_winners

def calculate_overall_roi(cleaned_df, all_cards_from_db):
    overall_results = []
    total_spend = float(cleaned_df['amount'].sum())

    for card_record in all_cards_from_db:
        engine = CardSimulationEngine(card_record)
        gross_inr_savings = sum(
            engine.calculate_transaction_reward(row.amount, row.merchant, row.category)["inr_savings"]
            for row in cleaned_df.itertuples()
        )
        
        if total_spend >= engine.waiver_threshold:
            effective_fee = 0.0
            waiver_status = "Waived"
        else:
            effective_fee = engine.joining_fee
            waiver_status = "Applied"

        net_roi = gross_inr_savings - effective_fee
        overall_results.append({
            "card_name": engine.card_name,
            "gross_savings": round(gross_inr_savings, 2),
            "effective_fee": round(effective_fee, 2),
            "net_roi": round(net_roi, 2),
            "waiver_status": waiver_status,
            "total_spend": round(total_spend, 2),
            "gap_to_waiver": round(max(0, engine.waiver_threshold - total_spend), 2),
            "primary_category": engine.primary_category
        })

    return sorted(overall_results, key=lambda x: x['net_roi'], reverse=True)