import pandas as pd

file_path = 'data/sample_uploads/transactions (2).xlsx'
df = pd.read_excel(file_path)

# 🚨 AUTO-FIX: Sabhi columns ko lowercase kar do aur spaces hata do
df.columns = df.columns.str.strip().str.lower()

if 'amount' not in df.columns:
    print(f"❌ ERROR: 'amount' column still not found! Available columns: {df.columns.tolist()}")
else:
    # 1. Biggest Transactions
    df_sorted = df.sort_values(by='amount', ascending=False)
    
    print("--- TOP 5 BIGGEST SPENDS (The Culprits) ---")
    # Merchant aur Category column names bhi check kar lena agar error aaye
    print(df_sorted.head(5))

    print("\n--- TOTAL SUM CHECK ---")
    total_sum = df['amount'].sum()
    print(f"Total Amount in Excel: {total_sum}")
    
    if total_sum > 200000:
        print("⚠️ ALERT: Your spend is over 2 Lakhs. This is why fees are being waived.")
    else:
        print("✅ Spend is under control.")