import pandas as pd
import numpy as np
import os

def parse_universal_bank_statement(file_path_or_buffer):
    """
    Returns DataFrame or raises a clear Error. No more hidden strings!
    """
    # 1. CHECK FOR THE FILE
    if isinstance(file_path_or_buffer, str) and not os.path.exists(file_path_or_buffer):
        raise FileNotFoundError(f"❌ File not found at specified path: {file_path_or_buffer}")

    # 2. RAW FILE READ (No Try-Except that returns strings)
    if str(file_path_or_buffer).endswith('.csv'):
        df_raw = pd.read_csv(file_path_or_buffer, header=None)
    else:
        df_raw = pd.read_excel(file_path_or_buffer, header=None)

    # 3. DYNAMIC HEADER HUNTER
    header_idx = -1
    for idx, row in df_raw.iterrows():
        row_str = ' '.join(row.dropna().astype(str)).lower()
        if 'date' in row_str and ('amount' in row_str or 'withdrawal' in row_str or 'debit' in row_str) and \
           ('narration' in row_str or 'transaction' in row_str or 'particulars' in row_str or 'description' in row_str):
            header_idx = idx
            break

    if header_idx == -1:
        raise ValueError("❌ Error: Couldn't find transactions table in the file. Please Check format!")

    # Slice and Clean
    df = df_raw.iloc[header_idx+1:].copy()
    df.columns = df_raw.iloc[header_idx].astype(str).str.strip().str.lower()
    df = df.loc[:, ~df.columns.duplicated()]

    # 4. COLUMN RADAR
    date_col = next((c for c in df.columns if 'date' in c), None)
    note_col = next((c for c in df.columns if any(k in c for k in ['narration', 'transaction', 'particulars', 'description'])), None)
    withdraw_col = next((c for c in df.columns if 'withdrawal' in c or 'debit' in c and 'type' not in c), None)
    type_col = next((c for c in df.columns if 'type' in c or 'cr/dr' in c), None)
    amount_col = next((c for c in df.columns if 'amount' in c and c != withdraw_col), None)

    if not date_col or not note_col:
        raise ValueError("❌ Error: Date ya Transaction Note wala column nahi mil raha.")

    # 5. THE 3-FORMAT PURGE
    df_filtered = pd.DataFrame()

    if withdraw_col:
        df['temp_amount'] = pd.to_numeric(df[withdraw_col].astype(str).str.replace(',', ''), errors='coerce')
        df_filtered = df[df['temp_amount'] > 0].copy()
        df_filtered['amount'] = df_filtered['temp_amount']
    elif type_col and amount_col: # Format 1: Type Column 
        # Convert to numeric and take ABSOLUTE value because 'Debit' label is already there
        df['val'] = pd.to_numeric(df[amount_col].astype(str).str.replace(',', ''), errors='coerce').abs()
        is_debit = df[type_col].astype(str).str.lower().str.contains('dr|debit')
        df_filtered = df[is_debit & (df['val'] > 0)].copy()
        df_filtered['amount'] = df_filtered['val']
    elif amount_col:
        df['temp_amount'] = pd.to_numeric(df[amount_col].astype(str).str.replace(',', ''), errors='coerce')
        df_filtered = df[df['temp_amount'] < 0].copy()
        df_filtered['amount'] = df_filtered['temp_amount'].abs()
    else:
        raise ValueError("❌ Error: Couldn't recognize bank format. Amount Column is missig, please check!")

    # Standardize Output
    df_final = df_filtered[[date_col, note_col, 'amount']].copy()
    df_final.columns = ['txn_date', 'txn_note', 'amount']
    return df_final.dropna()