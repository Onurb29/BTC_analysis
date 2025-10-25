import sqlite3
import pandas as pd
import os
import pandas_ta as ta  # or "import talib as ta"

# ----------------------
# 1. Load Data from DB
# ----------------------
# Dynamically determine the database path
script_dir = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(script_dir, "btc_analysis.db")

# Connect to SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Load data (just date + price for indicators)
df = pd.read_sql_query("""
    SELECT date, btc_price_usd
    FROM btc_indicators
    ORDER BY date ASC
""", conn)

# Convert to datetime for convenience
df['date'] = pd.to_datetime(df['date'])
df.sort_values(by='date', inplace=True)
df.set_index('date', inplace=True)

# ----------------------
# 2. Calculate Indicators
# ----------------------

# (A) Moving Average (e.g., 14-day MA)
df['ma14'] = df['btc_price_usd'].rolling(window=14).mean()

# (B) RSI (14-day default)
df['rsi'] = ta.rsi(df['btc_price_usd'], length=14)

# (C) Bollinger Bands (20-day window by default)
# Pandas TA will return columns bollinger_lband, bollinger_mavg, bollinger_hband
bbands = ta.bbands(df['btc_price_usd'], length=20, std=2)
df['bb_low'] = bbands['BBL_20_2.0']
df['bb_mid'] = bbands['BBM_20_2.0']
df['bb_high'] = bbands['BBU_20_2.0']

# Optional: Drop NaN rows at the start of dataset (indicators often need 'warm-up' periods)
df.dropna(inplace=True)

# ----------------------
# 3. Update Database
# ----------------------

# We'll add a few more columns to our original table if not already done.
# For demonstration, we show how to do it, but you may have to comment these out
# once they've run once, or wrap them in a try/except.
try:
    cursor.execute("ALTER TABLE btc_indicators ADD COLUMN ma14 REAL")
    cursor.execute("ALTER TABLE btc_indicators ADD COLUMN rsi REAL")
    cursor.execute("ALTER TABLE btc_indicators ADD COLUMN bb_low REAL")
    cursor.execute("ALTER TABLE btc_indicators ADD COLUMN bb_mid REAL")
    cursor.execute("ALTER TABLE btc_indicators ADD COLUMN bb_high REAL")
    conn.commit()
except:
    pass  # If the columns already exist, ignore the error

# Loop through df and update each row in the database
for date_idx, row in df.iterrows():
    date_str = date_idx.strftime('%Y-%m-%d')
    ma14_value = row['ma14']
    rsi_value = row['rsi']
    bb_low_value = row['bb_low']
    bb_mid_value = row['bb_mid']
    bb_high_value = row['bb_high']

    cursor.execute("""
        UPDATE btc_indicators
        SET ma14 = ?,
            rsi = ?,
            bb_low = ?,
            bb_mid = ?,
            bb_high = ?
        WHERE date = ?
    """, (ma14_value, rsi_value, bb_low_value, bb_mid_value, bb_high_value, date_str))

conn.commit()
conn.close()

print("Technical indicators computed and updated in the database!")
