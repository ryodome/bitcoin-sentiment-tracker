import streamlit as st
import datetime
import requests
import os
from dotenv import load_dotenv
from PIL import Image

# Load API keys from .env
load_dotenv()

# Set the page
st.set_page_config(page_title="Bitcoin Sentiment Tracker")

# Title and date
st.title("Bitcoin Sentiment Tracker")

# Optional: Bitcoin logo at the top
try:
    btc_image = Image.open("btc_logo.png")
    st.image(btc_image, width=40)
except:
    pass

# Today's date
today = datetime.date.today().strftime("%B %d, %Y")
st.subheader(f"Date: {today}")
st.markdown("---")

# Get BTC price from Coinbase
def get_btc_price():
    try:
        url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
        response = requests.get(url)
        data = response.json()
        price = float(data["data"]["amount"])
        return price
    except:
        return None

btc_price = get_btc_price()

# Get Bitcoin sentiment score from LunarCrush
def get_bitcoin_social_sentiment():
    try:
        api_key = os.getenv("LUNARCRUSH_API_KEY")
        url = "https://api.lunarcrush.com/v2"
        params = {
            "data": "assets",
            "key": api_key,
            "symbol": "BTC"
        }
        response = requests.get(url, params=params)
        data = response.json()
        score = data["data"][0]["galaxy_score"]
        return score
    except:
        return None

# Get sentiment score now
social_score = get_bitcoin_social_sentiment()

# Color-coded dropdowns
def colored_selectbox(label, options):
    color_map = {
        "Bullish": "🟢 Bullish",
        "Neutral": "🟡 Neutral",
        "Bearish": "🔴 Bearish",
        "Positive": "🟢 Positive",
        "Flat": "🟡 Flat",
        "Negative": "🔴 Negative"
    }
    colored_options = [color_map.get(opt, opt) for opt in options]
    selection = st.selectbox(label, colored_options)
    for k, v in color_map.items():
        if v == selection:
            return k
    return selection

# Layout
col1, col2 = st.columns(2)

with col1:
    news_sentiment = colored_selectbox("News Sentiment", ["Bullish", "Neutral", "Bearish"])
    twitter_sentiment = colored_selectbox("X (fka Twitter) Sentiment", ["Bullish", "Neutral", "Bearish"])
    etf_sentiment = colored_selectbox("ETF Flows", ["Positive", "Flat", "Negative"])

with col2:
    if btc_price is not None:
        st.metric(label="BTC Price (USD)", value=f"${btc_price:,.2f}")
        st.markdown("*Bitcoin price data via Coinbase*")
    else:
        st.metric("BTC Price (USD)", "Unavailable")

    if social_score is not None:
        st.markdown(f"**Social Sentiment Score:** {social_score}/100")
    else:
        st.markdown("Social Sentiment Score: Unavailable")

    custom_notes = st.text_area("Custom Summary or Notes", height=180)

# Calculate overall sentiment
def overall_sentiment(news, twitter, etf):
    score = 0
    sentiment_map = {
        "Bullish": 1,
        "Positive": 1,
        "Neutral": 0,
        "Flat": 0,
        "Bearish": -1,
        "Negative": -1
    }
    score += sentiment_map.get(news, 0)
    score += sentiment_map.get(twitter, 0)
    score += sentiment_map.get(etf, 0)

    if score >= 2:
        return "🟢 Bullish"
    elif score <= -2:
        return "🔴 Bearish"
    else:
        return "🟡 Neutral"


overall = overall_sentiment(news_sentiment, twitter_sentiment, etf_sentiment)

# Output block
st.markdown("---")
st.markdown("### Generated Snapshot")

if btc_price is not None:
    price_line = f"Bitcoin Price: ${btc_price:,.2f}"
else:
    price_line = "Bitcoin Price: Unavailable"

if social_score is not None:
    sentiment_line = f"Social Sentiment Score: {social_score}/100"
else:
    sentiment_line = "Social Sentiment Score: Unavailable"

output = f"""Date: {today}
{price_line}
{sentiment_line}
Bitcoin Sentiment: {overall}

News Sentiment: {news_sentiment}  
X (fka Twitter) Sentiment: {twitter_sentiment}  
ETF Flow Sentiment: {etf_sentiment}

Summary:  
{custom_notes if custom_notes else "Sentiment is mixed today. No major moves in ETF flows or headlines, while social media sentiment remains divided."}
"""

st.code(output, language="text")
st.download_button("Download Snapshot as .txt", output, file_name=f"btc_sentiment_snapshot_{today}.txt")

# Footer only (image removed)
st.caption("Built by Ryan with Vibes.")
