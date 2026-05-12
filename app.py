import streamlit as st
import requests
import pandas as pd

# =========================
# PAGE SETTINGS
# =========================

st.set_page_config(
    page_title="MNQ Bias Dashboard",
    layout="wide"
)

st.title("📈 MNQ Bias Dashboard")

# =========================
# API KEY
# =========================

API_KEY = st.secrets["FINNHUB_API_KEY"]

# =========================
# WATCHLIST
# =========================

WATCHLIST = {
    "NVDA": "NVIDIA",
    "MSFT": "Microsoft",
    "AAPL": "Apple",
    "META": "Meta",
    "AMZN": "Amazon",
    "GOOGL": "Google",
    "TSLA": "Tesla"
}

# =========================
# GET STOCK DATA
# =========================

def get_quote(symbol):

    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    return None

# =========================
# BUILD TABLE DATA
# =========================

data = []

for ticker, company in WATCHLIST.items():

    quote = get_quote(ticker)

    if quote:

        current_price = quote.get("c", 0)
        previous_close = quote.get("pc", 0)

        percent_change = 0

        if previous_close != 0:
            percent_change = (
                (current_price - previous_close)
                / previous_close
            ) * 100

        data.append({
            "Ticker": ticker,
            "Company": company,
            "Price": round(current_price, 2),
            "% Change": round(percent_change, 2)
        })

# =========================
# DATAFRAME
# =========================

df =df = pd.DataFrame(data)

st.subheader("🔥 Big Tech Watchlist")

if df.empty:

    st.error("No market data received from Finnhub API.")

else:

    st.dataframe(
        df,
        use_container_width=True
    )

    bullish = len(df[df["% Change"] > 0])
    bearish = len(df[df["% Change"] < 0])

    st.subheader("🧠 Market Bias")

    if bullish > bearish:

        st.success(
            f"🟢 Bullish Sentiment ({bullish} bullish vs {bearish} bearish)"
        )

    elif bearish > bullish:

        st.error(
            f"🔴 Bearish Sentiment ({bearish} bearish vs {bullish} bullish)"
        )

    else:

        st.warning("🟡 Neutral Market Sentiment")