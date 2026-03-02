# 🚀 Personalized Wealth-Maximizer (Credit Card Optimizer)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Gemini API](https://img.shields.io/badge/AI-Google_Gemini-orange.svg)
![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)

<img width="1919" height="779" alt="Screenshot 2026-03-01 211850" src="https://github.com/user-attachments/assets/170fa11b-777c-42ea-ac0c-45b380eca00e" />

## 📌 The Problem It Solves
Most AI financial tools act as generic "wrappers" that hallucinate mathematics and fail to understand the fine print of banking terms (like category exclusions or fee waivers). 

The **Personalized Wealth-Maximizer** is a deterministic, AI-powered financial engine. It ingests raw bank statements, applies strict semantic tagging, and calculates exact, real-world credit card ROI without mathematical hallucinations.

## 📺 Live Demo

* **Full Video Demonstration (~6 mins):** [https://youtu.be/x7m3gAh_9BY]
*(Highly recommended: Showcases the 100% mathematical accuracy and edge-case handling of the Titanium Backend running locally).*
---

## 🛡️ The "Titanium" Architecture (Key Features)

This project avoids AI unreliability by separating the **Language Engine** from the **Math Engine**.

* **Privacy-First Strict ID-Mapping:** Transaction amounts are NEVER sent to the LLM. The AI only receives isolated merchant strings to generate category tags. The backend reconstructs the data securely, ensuring absolute data privacy.
* **Deterministic AI (0.0 Temperature):** The LLM is locked at a 0.0 temperature constraint. It does not "guess" categories; it categorizes them based on rigid, predefined parameters for 100% consistency.
* **Hard-Coded Financial Guardrails:** The math engine understands bank exclusions. For example, it correctly maps a 0% reward rate for Utility/Rent payments on the SBI Cashback card, while calculating the 1% margin for HDFC Millennia.
* **Smart P2P Filtering:** Automatically isolates and ignores non-rewardable UPI transfers (Peer-to-Peer) to prevent artificial ROI inflation.
* **Contextual Wealth Advisor:** An integrated chat agent that cross-references user queries (e.g., travel plans) strictly with their past spending data to offer realistic advice, falling back to pure mathematical ROI when qualitative perks (like lounges) cannot be quantified.

---

## 🛠️ Technical Stack

* **Frontend:** Streamlit (for a responsive, interactive dashboard)
* **Backend Logic:** Python, Pandas (Data processing, joining, and aggregation)
* **AI/NLP Layer:** Google Gemini Flash API (Semantic merchant tagging)
* **Environment:** Python `dotenv` for secure credential management

---

## 💻 Local Setup & Installation

Follow these steps to run the Personalized Wealth-Maximizer securely on your local machine:

**1. Clone the repository**
`git clone https://github.com/hitanshu04/credit-card-optimizer.git`
`cd credit-card-optimizer`

**2. Create a Virtual Environment (Recommended)**
`python -m venv venv`
`source venv/bin/activate` *(On Windows use: `venv\Scripts\activate`)*

**3. Install Dependencies**
`pip install -r requirements.txt`

**4. Configure Environment Variables**
Create a `.env` file in the root directory and add your Google Gemini API key:
`GEMINI_API_KEY="your_api_key_here"`
*(Note: Do not commit your `.env` file. Ensure it is listed in `.gitignore`.)*

**5. Run the Application**
`streamlit run app.py`

**Note on Data Ingestion: The engine currently bypasses live URL scraping to maintain sub-second latency and mathematical stability. All core rules for the 6 target cards have been pre-hydrated into the JSON Ground Truth layer.**

---

## ⚙️ How It Works (The Pipeline)

1. **Ingestion:** User uploads a raw `.xlsx` bank statement.
2. **Batch Processing:** Data is batched and sent to the LLM for context-aware tagging (Shopping, Travel, Utilities, P2P).
3. **Reconstruction:** Tags are mapped back to the original local dataframe via unique IDs.
4. **Policy Engine Execution:** The tagged data is run through the credit card database to calculate Net ROI, factoring in annual fees and spend-based waivers.
5. **Visualization:** Results are rendered across dynamic UI tabs showing top performers, category breakdowns, and an audit trail.

---

## 🔒 Confidentiality Notice
This repository contains the source code for an independent architecture project. Certain proprietary datasets and keys have been excluded via `.gitignore` to maintain security best practices.
