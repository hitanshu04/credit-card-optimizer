import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# --- 1. STRICT BACKEND IMPORTS (Existing flawless layers) ---
from src.database.connection import SessionLocal
from src.database.models import CreditCard
from src.engine.excel_parser import parse_universal_bank_statement
from src.engine.transaction_tagger import tag_transactions_with_ai
from src.engine.calculator import find_category_specialists, calculate_overall_roi
from src.agent.chat_agent import get_financial_advice

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Wealth Maximizer AI", page_icon="🚀", layout="wide")

# Load environment variables

if "GEMINI_API_KEY" in st.secrets:
    # Runs when deployed on Streamlit Cloud
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Runs on your local machine
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

# --- 3. SESSION STATE MANAGEMENT (The Vault to save API Quota) ---
if 'pipeline_run_complete' not in st.session_state:
    st.session_state['pipeline_run_complete'] = False
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# --- 4. THE UI LAYOUT ---
st.title("🚀 Personalized Wealth-Maximizer Dashboard")
st.markdown("Upload your bank statement and let our Titanium AI engine optimize your credit card rewards.")

# SIDEBAR: Control Room
with st.sidebar:
    st.header("⚙️ Control Panel")
    uploaded_file = st.file_uploader("Upload Bank Statement (.csv or .xlsx)", type=["csv", "xlsx"])
    
    if st.button("Reset Dashboard"):
        st.session_state.clear()
        st.rerun()

# --- 5. THE EXECUTION ENGINE (Runs only once per upload) ---
if uploaded_file is not None and not st.session_state['pipeline_run_complete']:
    try:
        # Safe File Handling: Save to temp file to respect your parser's strict checks
        file_ext = uploaded_file.name.split('.')[-1]
        temp_path = f"temp_upload.{file_ext}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.status("🚀 Running Titanium AI Pipeline...", expanded=True) as status:
            st.write("📥 [1/5] Loading and Parsing Transactions...")
            raw_df = parse_universal_bank_statement(temp_path)
            
            st.write("🏷️ [2/5] Tagging Transactions via AI (Strict ID-Mapping)...")
            tagged_df = tag_transactions_with_ai(raw_df, api_key=api_key)
            
            st.write("📡 [3/5] Fetching Live Card Data from Database...")
            db = SessionLocal()
            db_cards = db.query(CreditCard).all()
            
            st.write("🧮 [4/5] Running Math Engine & ROI Analysis...")
            cat_winners = find_category_specialists(tagged_df, db_cards)
            roi_ranking = calculate_overall_roi(tagged_df, db_cards)
            
            total_spend = float(tagged_df['amount'].sum())
            spending_map = tagged_df.groupby('category')['amount'].sum().to_dict()

            # Pack results safely
            math_results = {
                "category_winners": cat_winners,
                "overall_roi_ranking": roi_ranking,
                "category_spending_map": spending_map, 
                "total_tracked_spend": total_spend      
            }

            # Lock data in Session State
            st.session_state['math_results'] = math_results
            st.session_state['tagged_df'] = tagged_df
            st.session_state['db_cards'] = db_cards
            st.session_state['pipeline_run_complete'] = True
            
            status.update(label="✅ Pipeline Execution Complete!", state="complete", expanded=False)

    except Exception as e:
        st.sidebar.error(f"❌ Pipeline Error: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()
        if os.path.exists(temp_path):
            os.remove(temp_path) # Clean up temp file

# --- 6. THE GRAND PRESENTATION (TABS) ---
if st.session_state['pipeline_run_complete']:
    
    # Retrieve data from the vault
    math_results = st.session_state['math_results']
    tagged_df = st.session_state['tagged_df']
    
    # Create 4 Clean Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Top Cards & ROI", 
        "📊 Category Insights", 
        "🧾 Smart Statement", 
        "💬 AI Wealth Advisor"
    ])

    # === TAB 1: THE OVERALL PROFIT CHAMPIONS ===
    with tab1:
        st.subheader("Your Top 3 Recommended Cards")
        top_3_roi = math_results.get('overall_roi_ranking', [])[:3]
        total_spend = math_results.get('total_tracked_spend', 0)
        
        for i, card in enumerate(top_3_roi, 1):
            net_profit = card.get('net_roi', 0.0)
            card_name = card.get('card_name', 'Card')
            
            if i == 1:
                st.success(f"🥇 **THE ABSOLUTE WINNER: {card_name}**")
                st.write(f"- Out of your total account debits of **₹{total_spend:,.2f}** (which helped waive your annual fees!), this card maximized rewards on your eligible shopping.")
                st.write(f"- It puts **₹{net_profit:,.2f}** back into your pocket after all fees.")
            else:
                st.info(f"🥈 **Rank #{i}: {card_name}**")
                st.write(f"- A great backup card saving you **₹{net_profit:,.2f}** overall.")

    # === TAB 2: CATEGORY-WISE OPTIMIZATION ===
    with tab2:
        st.subheader("Where exactly are you saving money?")
        cat_winners = math_results.get('category_winners', {})
        spending_map = math_results.get('category_spending_map', {})

        for cat, data in cat_winners.items():
            actual_spend = spending_map.get(cat, 0) 
            best_card = data.get('winner', 'Unknown Card')
            savings = data.get('savings', 0.0)
            
            if actual_spend > 0:
                effective_price = actual_spend - savings
                with st.expander(f"🔹 {cat} (Spent: ₹{actual_spend:,.2f})"):
                    st.write(f"If you had used the **{best_card}**, you would have saved **₹{savings:,.2f}**.")
                    st.write(f"✅ **Result:** You could have completed your {cat} purchases in only **₹{effective_price:,.2f}**!")
                    st.caption("💡 Advisor Note: That's a direct reduction in your monthly expenses.")

    # === TAB 3: THE SMART STATEMENT ===
    with tab3:
        st.subheader("Detailed Transactions & Tags")
        st.markdown("Review how our AI accurately categorized your expenses. (P2P/Ignored earn 0% rewards to protect your ROI accuracy).")
        
        # Display clean dataframe
        display_df = tagged_df[['txn_date', 'txn_note', 'category', 'amount']].copy()
        # Ensure amounts are readable
        display_df['amount'] = display_df['amount'].apply(lambda x: f"₹{x:,.2f}")
        
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )

    # === TAB 4: AI CHAT AGENT ===
    with tab4:
        st.subheader("💬 Ask Your AI Advisor")
        st.markdown("Ask why a specific card won, or inquire about the math behind your savings.")
        
        # # Display chat history
        # for message in st.session_state['chat_history']:
        #     with st.chat_message(message["role"]):
        #         st.markdown(message["content"])

        # # Chat Input
        # if prompt := st.chat_input("E.g., Why did CASHBACK SBI beat Amazon Pay ICICI?"):
        #     # Display user message
        #     with st.chat_message("user"):
        #         st.markdown(prompt)
            
        #     # Append to history
        #     st.session_state['chat_history'].append({"role": "user", "content": prompt})
            
        #     # Prepare DB context for the agent
        #     db_context = [
        #         {column.name: str(getattr(card, column.name)) for column in card.__table__.columns}
        #         for card in st.session_state['db_cards']
        #     ]
            
        #     # Fetch and display AI response
        #     with st.chat_message("assistant"):
        #         with st.spinner("Analyzing your financial data..."):
        #             response = get_financial_advice(
        #                 prompt, 
        #                 st.session_state['math_results'], 
        #                 db_context, 
        #                 st.session_state['chat_history'], 
        #                 api_key
        #             )
        #         st.markdown(response)
            
        #     # Append to history
        #     st.session_state['chat_history'].append({"role": "assistant", "content": response})

        # 1. Chat History Container (Fixed height creates the scroll effect)
        chat_container = st.container(height=500) 

        with chat_container:
            for message in st.session_state['chat_history']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # 2. Chat Input (Placed directly inside Tab 4)
        if prompt := st.chat_input("E.g., Why did CASHBACK SBI beat Amazon Pay ICICI?"):
            # Append user message to history
            st.session_state['chat_history'].append({"role": "user", "content": prompt})
            
            # Show user message immediately in container
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            # Prepare DB context
            db_context = [
                {column.name: str(getattr(card, column.name)) for column in card.__table__.columns}
                for card in st.session_state['db_cards']
            ]
            
            # Assistant Response Logic
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing..."):
                        response = get_financial_advice(
                            prompt, 
                            st.session_state['math_results'], 
                            db_context, 
                            st.session_state['chat_history'], 
                            api_key
                        )
                        st.markdown(response)
            
            # Append assistant message to history
            st.session_state['chat_history'].append({"role": "assistant", "content": response})
            
            # Force rerun to sync state and keep user on the same tab
            st.rerun()