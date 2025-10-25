import requests
import sqlite3
import os
from datetime import datetime

# Database file path
script_dir = os.path.dirname(os.path.abspath(__file__))  # Corrected variable name
db_file = os.path.join(script_dir, "btc_analysis.db")

def fetch_metrics(asset, metrics, start_date, end_date):
    """
    Fetch metrics from the Coin Metrics Community API.
    """
    base_url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
    params = {
        "assets": asset,
        "metrics": ",".join(metrics),
        "frequency": "1d",
        "start_time": start_date,
        "end_time": end_date,
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return {"data": []}

def store_data_to_db(data):
    """
    Store fetched data into SQLite database.
    """
    try:
        conn = sqlite3.connect(db_file)  # Use corrected `db_file` variable
        cursor = conn.cursor()

        # Create table for on-chain data if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS btc_onchain (
            date TEXT PRIMARY KEY,
            tx_count INTEGER,
            active_addresses INTEGER,
            hash_rate REAL,
            difficulty REAL
        )
        """)

        # Insert or update records
        for entry in data.get("data", []):
            date = entry.get("time", "")[:10]  # Extract YYYY-MM-DD
            tx_count = int(entry["TxTfrCnt"]) if "TxTfrCnt" in entry else None
            active_addresses = int(entry["AdrActCnt"]) if "AdrActCnt" in entry else None
            hash_rate = float(entry["HashRate"]) if "HashRate" in entry else None
            difficulty = float(entry["DiffMean"]) if "DiffMean" in entry else None

            # Insert or update the record
            cursor.execute("""
            INSERT OR REPLACE INTO btc_onchain (date, tx_count, active_addresses, hash_rate, difficulty)
            VALUES (?, ?, ?, ?, ?)
            """, (date, tx_count, active_addresses, hash_rate, difficulty))

        conn.commit()
        print(f"Successfully updated database with {len(data.get('data', []))} records.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def main():
    # Define parameters for the API request
    asset = "btc"
    metrics = ["TxTfrCnt", "AdrActCnt", "HashRate", "DiffMean"]
    start_date = "2024-12-30"
    end_date = "2025-01-02"

    # Fetch data from Coin Metrics
    print("Fetching on-chain metrics from Coin Metrics...")
    data = fetch_metrics(asset, metrics, start_date, end_date)

    # Check if data is returned
    if not data.get("data"):
        print("No data fetched. Exiting.")
        return

    # Store the data in SQLite
    print("Storing data into SQLite database...")
    store_data_to_db(data)

if __name__ == "__main__":
    main()
