import streamlit as st
import datetime
import requests
from PIL import Image

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

# Get BTC price + 24h change
def get_btc_price_and_change():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&tickers=false&market_data=true"
        response = requests.get(url)
        data = response.json()
        price = data["market_data"]["current_price"]["usd"]
        change = data["market_data"]["price_change_percentage_24h"]
        return price, change
    except:
        return None, None

btc_price, btc_change = get_btc_price_and_change()

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
    if btc_price is not None and btc_change is not None:
        st.metric(
            label="BTC Price (USD)",
            value=f"${btc_price:,.2f}",
            delta=f"{btc_change:+.2f}%",
            delta_color="normal"
        )
    else:
        st.metric("BTC Price (USD)", "Unavailable")

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
    score += sentiment_map[news]
    score += sentiment_map[twitter]
    score += sentiment_map[etf]
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

output = f"""Date: {today}
Bitcoin Price: ${btc_price:,.2f} ({btc_change:+.2f}%)
Bitcoin Sentiment: {overall}

News Sentiment: {news_sentiment}  
X (fka Twitter) Sentiment: {twitter_sentiment}  
ETF Flow Sentiment: {etf_sentiment}

Summary:  
{custom_notes if custom_notes else "Sentiment is mixed today. No major moves in ETF flows or headlines, while social media sentiment remains divided."}
"""

st.code(output, language="text")
st.download_button("Download Snapshot as .txt", output, file_name=f"btc_sentiment_snapshot_{today}.txt")

# Footer + vibecoding image
st.caption("Built by Ryan with Vibes.")
try:
    vibe_img = Image.open("Vibecoding.png")
    st.image(vibe_img, width=150)
except:
    st.warning("Add 'Vibecoding.png' to display the closing vibe.")

