# visualize_btc.py
import os
import sqlite3
import humanize
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(script_dir, "btc_analysis.db")
reports_dir = os.path.join(script_dir, "reports")
os.makedirs(reports_dir, exist_ok=True)

# Load data
with sqlite3.connect(db_file) as conn:
    df = pd.read_sql_query("""
        SELECT
            date,
            fear_greed_value,
            btc_price_usd,
            btc_market_cap_usd,
            volume_usd
        FROM btc_indicators
        ORDER BY date
    """, conn)

# Parse date and clean
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.sort_values("date").dropna(subset=["date"])

# --- Figure 1: Fear & Greed vs BTC Price ---
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df["date"],
    y=df["btc_price_usd"],  # keep numeric
    mode="markers",
    marker=dict(
        size=8,
        color=df["fear_greed_value"],
        colorscale="RdYlGn",
        showscale=True,
        colorbar=dict(title="Fear & Greed")
    ),
    name="BTC Price",
    hovertemplate=(
        "Date: %{x|%Y-%m-%d}<br>"
        "Price: $%{y:,.2f}<br>"
        "Fear & Greed: %{marker.color}<extra></extra>"
    )
))
fig1.update_layout(
    title="Fear & Greed Index vs Bitcoin Price",
    xaxis_title="Date",
    yaxis_title="BTC Price (USD)",
    template="plotly_dark",
    height=600
)

# --- Figure 2: Market Cap & Volume (dual axis) ---
fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(go.Scatter(
    x=df["date"], y=df["btc_market_cap_usd"],
    mode="lines+markers", name="Market Cap",
    hovertemplate=(
        "Date: %{x|%Y-%m-%d}<br>"
        "Market Cap: " + "%{customdata}" + "<extra></extra>"
    ),
    customdata=df["btc_market_cap_usd"].apply(lambda v: humanize.intword(v) if pd.notnull(v) else "N/A")
), secondary_y=False)

fig2.add_trace(go.Scatter(
    x=df["date"], y=df["volume_usd"],
    mode="lines+markers", name="Volume",
    hovertemplate=(
        "Date: %{x|%Y-%m-%d}<br>"
        "Volume: " + "%{customdata}" + "<extra></extra>"
    ),
    customdata=df["volume_usd"].apply(lambda v: humanize.intword(v) if pd.notnull(v) else "N/A")
), secondary_y=True)

fig2.update_layout(
    title="Bitcoin Market Cap and Volume Over Time",
    xaxis_title="Date",
    template="plotly_dark",
    height=600
)
fig2.update_yaxes(title_text="Market Cap (USD)", secondary_y=False)
fig2.update_yaxes(title_text="Volume (USD)", secondary_y=True)

# Show and save
fig1.show()
fig2.show()
fig1.write_html(os.path.join(reports_dir, "fg_vs_price.html"))
fig2.write_html(os.path.join(reports_dir, "mcap_volume.html"))
print("Saved reports to:", reports_dir)