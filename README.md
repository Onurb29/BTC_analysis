# 🪙 Bitcoin Analysis Project

This project was developed independently as a personal data engineering and analytics project — combining API integration, database management, and data visualization in Python.

It collects and analyzes **Bitcoin market, on-chain, and sentiment data** using public APIs.
All data is stored locally in an **SQLite database**, processed using Python, and visualized with Plotly.

---

## 📊 Features

* Fetches Bitcoin market data (price, volume, market cap) from the **CoinGecko API**
* Retrieves sentiment data (Fear & Greed Index) from **Alternative.me**
* Stores all data in a **local SQLite database** (`btc_analysis.db`)
* Computes daily averages and indicators
* Generates readable reports and interactive visualizations using **Plotly**

---

## 🧮 Tech Stack

* **Python 3.11+**
* **SQLite (Local Database)** – lightweight and built into Python
* **DB Browser for SQLite** – recommended GUI for exploring data
* **APIs:** CoinGecko, Alternative.me
* **Libraries:** `requests`, `pandas`, `plotly`, `humanize`

---

## ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/BTC_ANALYSIS.git
   cd BTC_ANALYSIS
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the main pipeline**

   ```bash
   python btc_data_pipeline.py
   ```

The script will automatically:

* Create the SQLite database file (`btc_analysis.db`) in the project folder
* Create tables if they don’t exist
* Fetch and insert live data from the APIs

---

## 🧮 Viewing the Database

You can explore and query your local database visually using **[DB Browser for SQLite](https://sqlitebrowser.org/)**.

**Steps:**

1. Open **DB Browser for SQLite**
2. Go to **File → Open Database…** and select `btc_analysis.db`
3. Use the **Browse Data** tab to inspect tables (`btc_indicators`, `btc_onchain`, etc.)
4. Use the **Execute SQL** tab to run custom queries or test calculations

---

## 🚀 Future Improvements

* Add on-chain metric correlation analysis (price vs. network activity)
* Migrate SQLite to a cloud-hosted MySQL database for multi-user access
* Build a Streamlit or Dash dashboard for real-time visualization

---

## 👤 Author

**Jimmy Perron**
*Analyst – Technical Systems | Industrial IT & Data Engineering*
[GitHub Profile](https://github.com/Onurb29)

<img width="1706" height="593" alt="image" src="https://github.com/user-attachments/assets/6dfe31a6-340f-481f-a75f-f317615d62ca" />

