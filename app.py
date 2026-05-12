import streamlit as st
import requests
import pandas as pd
import yfinance as yf

# =========================
# PAGE SETTINGS
# =========================

st.set_page_config(
    page_title="MNQ Intraday Dashboard",
    layout="wide"
)

# =========================
# TITLE
# =========================

st.title("📈 MNQ Intraday Trading Dashboard")

st.write(
    "Live intraday dashboard with NQ futures levels, market bias, economic calendar, and news."
)

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
    "TSLA": "Tesla",
    "SPY": "S&P 500 ETF",
    "QQQ": "Nasdaq ETF"
}

# =========================
# GET STOCK DATA
# =========================

def get_quote(symbol):

    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"

    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        return response.json()

    return None

# =========================
# GET MARKET NEWS
# =========================

def get_market_news():

    url = f"https://finnhub.io/api/v1/news?category=general&token={API_KEY}"

    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        return response.json()

    return []

# =========================
# MARKET OVERVIEW
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

df = pd.DataFrame(data)

st.subheader("🔥 Market Overview")

if df.empty:

    st.error("No market data received.")

else:

    st.dataframe(
        df,
        use_container_width=True
    )

# =========================
# INTRADAY BIAS ENGINE
# =========================

st.subheader("🧠 Intraday Bias Engine")

bullish = len(df[df["% Change"] > 0])
bearish = len(df[df["% Change"] < 0])

tech_strength = len(
    df[
        (df["Ticker"].isin([
            "NVDA",
            "AAPL",
            "MSFT",
            "META",
            "AMZN",
            "GOOGL"
        ]))
        &
        (df["% Change"] > 0)
    ]
)

if bullish > bearish and tech_strength >= 4:

    st.success(
        "🟢 Bullish MNQ Bias — Strong tech participation."
    )

elif bearish > bullish:

    st.error(
        "🔴 Bearish MNQ Bias — Weak market breadth."
    )

else:

    st.warning(
        "🟡 Neutral / Mixed Market Conditions."
    )

# =========================
# LIVE NQ FUTURES LEVELS
# =========================

st.subheader("📊 Live NQ Futures Levels")

try:

    nq = yf.Ticker("NQ=F")

    hist = nq.history(period="1mo")

    current_price = hist["Close"].iloc[-1]

    previous_day = hist["Close"].iloc[-2]

    previous_week = hist["Close"].iloc[-6]

    previous_month = hist["Close"].iloc[0]

    def get_bias(current, previous):

        if current > previous:
            return "🟢 Bullish"

        elif current < previous:
            return "🔴 Bearish"

        else:
            return "🟡 Neutral"

    levels_data = {
        "Timeframe": [
            "Previous Day",
            "Previous Week",
            "Previous Month"
        ],

        "Reference Price": [
            round(previous_day, 2),
            round(previous_week, 2),
            round(previous_month, 2)
        ],

        "Current Price": [
            round(current_price, 2),
            round(current_price, 2),
            round(current_price, 2)
        ],

        "Bias": [
            get_bias(current_price, previous_day),
            get_bias(current_price, previous_week),
            get_bias(current_price, previous_month)
        ]
    }

    levels_df = pd.DataFrame(levels_data)

    st.dataframe(
        levels_df,
        use_container_width=True
    )

except Exception as e:

    st.error(f"Error loading NQ futures data: {e}")

# =========================
# ECONOMIC CALENDAR
# =========================

st.subheader("📅 Economic Calendar")

economic_data = [
    {
        "Event": "CPI",
        "Actual": 3.4,
        "Forecast": 3.5,
        "Previous": 3.7,
        "Impact": "🔴 High"
    },
    {
        "Event": "Core CPI",
        "Actual": 3.6,
        "Forecast": 3.7,
        "Previous": 3.9,
        "Impact": "🔴 High"
    },
    {
        "Event": "NFP",
        "Actual": 175,
        "Forecast": 160,
        "Previous": 210,
        "Impact": "🔴 High"
    },
    {
        "Event": "Unemployment",
        "Actual": 4.0,
        "Forecast": 3.9,
        "Previous": 3.8,
        "Impact": "🟡 Medium"
    }
]

econ_df = pd.DataFrame(economic_data)

st.dataframe(
    econ_df,
    use_container_width=True
)

# =========================
# ECONOMIC GRAPH
# =========================

st.subheader("📈 Economic Comparison")

chart_data = econ_df.set_index("Event")[[
    "Actual",
    "Forecast",
    "Previous"
]]

st.bar_chart(chart_data)

# =========================
# SESSION TRACKING
# =========================

st.subheader("🌏 Session Tracking")

session_data = {
    "Session": [
        "Asia High",
        "Asia Low",
        "London High",
        "London Low",
        "Premarket High",
        "Premarket Low"
    ],
    "Level": [
        21890,
        21740,
        21980,
        21810,
        22025,
        21895
    ]
}

session_df = pd.DataFrame(session_data)

st.dataframe(
    session_df,
    use_container_width=True
)

# =========================
# MARKET NEWS
# =========================

st.subheader("📰 Market News")

news = get_market_news()

if len(news) == 0:

    st.warning("No news available.")

else:

    for article in news[:5]:

        st.markdown(
            f"### {article['headline']}"
        )

        st.write(
            f"Source: {article['source']}"
        )

        st.write(
            article['summary']
        )

        st.markdown(
            f"[Read Article]({article['url']})"
        )

        st.divider()