import sqlite3
import requests
from datetime import datetime
import os
import humanize

# Dynamically determine the database path
script_dir = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(script_dir, "btc_analysis.db")

# Connect to SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create a table for all indicators if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS btc_indicators (
    date TEXT PRIMARY KEY,
    fear_greed_value INTEGER,
    fear_greed_classification TEXT,
    btc_price_usd REAL,
    btc_market_cap_usd REAL,
    volume_usd REAL,
    opening_price REAL,
    closing_price REAL,
    average_price REAL
)
""")

# Variable to control the number of days to query
days_to_query = 90  # Change this value as needed

# Fetch Fear and Greed Index for the specified range
print(f"Fetching Fear and Greed Index data for the last {days_to_query} days...")
fng_url = f"https://api.alternative.me/fng/?limit={days_to_query}"
fng_data = requests.get(fng_url).json()["data"]

# Fetch Bitcoin price, market cap, and volume from CoinGecko
print(f"Fetching Bitcoin market data for the last {days_to_query} days...")
btc_market_chart_url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days_to_query}"
btc_data = requests.get(btc_market_chart_url).json()

# Check if the response contains the expected keys
if "prices" not in btc_data or "market_caps" not in btc_data or "total_volumes" not in btc_data:
    print("Error: Missing expected keys in the API response. Full response:")
    print(btc_data)
    exit(1)

# Process Bitcoin price, market cap, and volume data
btc_opening_prices = {}
btc_closing_prices = {}
btc_average_prices = {}
btc_market_caps = {}
btc_volumes = {}
btc_all_prices = {}

for entry in btc_data["prices"]:
    timestamp = entry[0] // 1000
    date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    price = entry[1]
    
    if date not in btc_opening_prices:
        btc_opening_prices[date] = price  # First entry for the day
    btc_closing_prices[date] = price  # Last entry for the day
    btc_all_prices.setdefault(date, []).append(price)  # Collect prices for average calculation

for date, prices in btc_all_prices.items():
    btc_average_prices[date] = sum(prices) / len(prices)

btc_market_caps = {datetime.fromtimestamp(entry[0] // 1000).strftime("%Y-%m-%d"): entry[1] for entry in btc_data["market_caps"]}
btc_volumes = {datetime.fromtimestamp(entry[0] // 1000).strftime("%Y-%m-%d"): entry[1] for entry in btc_data["total_volumes"]}

# Insert data into the SQLite database
print("Inserting data into SQLite database...")
for entry in fng_data:
    # Extract Fear and Greed data
    date = datetime.fromtimestamp(int(entry["timestamp"])).strftime("%Y-%m-%d")
    fear_greed_value = int(entry["value"])
    fear_greed_classification = entry["value_classification"]

    # Get corresponding Bitcoin data
    average_price = btc_average_prices.get(date, None)
    market_cap = btc_market_caps.get(date, None)
    volume = btc_volumes.get(date, None)
    opening_price = btc_opening_prices.get(date, None)
    closing_price = btc_closing_prices.get(date, None)

    # Insert or update the record in the SQLite database
    cursor.execute("""
    INSERT OR REPLACE INTO btc_indicators (
        date, fear_greed_value, fear_greed_classification, btc_price_usd, 
        btc_market_cap_usd, volume_usd, opening_price, closing_price, average_price
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, fear_greed_value, fear_greed_classification, average_price,
          market_cap, volume, opening_price, closing_price, average_price))

# Commit changes
conn.commit()

# Fetch and format data for readability
cursor.execute("""
SELECT date, 
       btc_price_usd, 
       btc_market_cap_usd, 
       volume_usd, 
       fear_greed_value, 
       fear_greed_classification,
       opening_price,
       closing_price,
       average_price
FROM btc_indicators
ORDER BY date
""")
rows = cursor.fetchall()

# Output formatted results with humanized numbers
print("Formatted Data (Market Cap, Volume, and Prices in Human-Readable Format):")
for row in rows:
    date, price, market_cap, volume, fear_greed, sentiment, opening, closing, average = row
    # Handle None values gracefully
    price_str = f"${price:,.2f}" if price is not None else "N/A"
    market_cap_str = humanize.intword(market_cap) if market_cap is not None else "N/A"
    volume_str = humanize.intword(volume) if volume is not None else "N/A"
    opening_str = f"${opening:,.2f}" if opening is not None else "N/A"
    closing_str = f"${closing:,.2f}" if closing is not None else "N/A"
    average_str = f"${average:,.2f}" if average is not None else "N/A"
    
    print(f"Date: {date}, Opening: {opening_str}, Closing: {closing_str}, Average: {average_str}, "
          f"Price: {price_str}, Market Cap: {market_cap_str}, Volume: {volume_str}, "
          f"Fear & Greed: {fear_greed}, Sentiment: {sentiment}")

# Close connection
conn.close()
print("Database connection closed.")
