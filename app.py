import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import numpy as np
from binance.client import Client
import matplotlib.pyplot as plt
import os
import asyncio
import websockets
import requests
import random


st.title("🚀 Live Crypto Price & Chart Tracker")
IMAGE_FOLDER = "popular_coin_images"



st.sidebar.title("Menu")
client = Client("", "")
page = st.sidebar.radio("Go To : ",["Home","Chart","News","About"])



if page == "Home":    
    def load_price_data():
        try:
            with open("price_data.json", "r") as file:
                return json.load(file)  
        except FileNotFoundError:
            return []  

# Function: Save price data to file
    def save_price_data(data):
        with open("price_data.json", "w") as file:
            json.dump(data, file)
            
    
# User Input
    symbol = st.text_input("Enter Coin Symbol (e.g., BTCUSDT):", "BTCUSDT").upper()
    klines = client.get_klines(symbol = symbol,interval = Client.KLINE_INTERVAL_1DAY,limit=7)
    if "image_path" in st.session_state and st.session_state["image_path"]:
        st.image(st.session_state["image_path"], width=150)

# Load Old Prices
    price_list = load_price_data()
    
                  
# Create Placeholders
    price_placeholder = st.empty()    
    # Start Live Update
    if st.button("Start Live Price & Chart Update"):
        # Create DataFrame
        df = pd.DataFrame(klines, columns=['Time', 'Open', 'Close', 'High', 'Low', 'Volume', '_', '_', '_', '_', '_', '_'])

        # Convert 'Close' to float
        df['Close'] = df['Close'].astype(float)

        # Calculate 20-day SMA and EMA
        df['SMA_20'] = df['Close'].rolling(window=20).mean()  # 20 days SMA
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()  # 20 days EMA

        # Create Plotly figure
        fig = go.Figure()

        # Closing Price Line
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Close'], mode='lines', name='Closing Price', line=dict(color='orange')))

        # 20-Day SMA Line
        fig.add_trace(go.Scatter(x=df['Time'], y=df['SMA_20'], mode='lines', name='20-Day SMA', line=dict(color='blue', dash='dash')))

        # 20-Day EMA Line
        fig.add_trace(go.Scatter(x=df['Time'], y=df['EMA_20'], mode='lines', name='20-Day EMA', line=dict(color='red')))

        # Layout customization
        fig.update_layout(
        title=f"Price Trends with SMA & EMA",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        template="plotly_dark",
        hovermode="x unified"
        )

# Streamlit code to display the plot
        st.title("Stock Price with SMA and EMA")
        st.plotly_chart(fig)
        
        def support_resistance_levels(data):
            high_prices = data['High'].astype(float)
            low_prices = data["Low"].astype(float)
            support = np.percentile(low_prices, 10)  # 10th percentile for support
            resistance = np.percentile(high_prices, 90)  # 90th percentile for resistance
            return support, resistance
        support, resistance = support_resistance_levels(df)
        
        # Display support and resistance levels
        st.title(f"Stock Price with Support & Resistance Levels")
        st.write(f"Support Level: {support}")
        st.write(f"Resistance Level: {resistance}")

# Create Plotly figure
        fig = go.Figure()

# Closing Price Line
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Close'], mode='lines', name='Closing Price', line=dict(color='green')))

# Support Level Line
        fig.add_trace(go.Scatter(x=df['Time'], y=[support] * len(df), mode='lines', name='Support Level', line=dict(color='green', dash='dot')))

# Resistance Level Line
        fig.add_trace(go.Scatter(x=df['Time'], y=[resistance] * len(df), mode='lines', name='Resistance Level', line=dict(color='red', dash='dot')))

# Layout Customization
        fig.update_layout(
        title="Price with Support & Resistance Levels",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        template="plotly_dark",
        hovermode="x unified"
        )

# Display the plot in Streamlit
        st.plotly_chart(fig)
        
        
        image_filename = f"{symbol}.png"
        image_full_path = os.path.join(IMAGE_FOLDER, image_filename)
                
        if os.path.exists(image_full_path):
            st.session_state["image_path"] = image_full_path  # Save image path in session
        else:
            st.error("⚠️ Coin image not found!")
            st.session_state["image_path"] = None
        
                
        while True:
            try:
                # Fetch Live Price
                price_data = client.get_symbol_ticker(symbol=symbol)
                price = float(price_data["price"])
                price_list.append(price)  

                # Save Updated Prices
                save_price_data(price_list)
                
                

            # ✅ Update Price Display
                price_placeholder.markdown(
                 f"### 💰 Live {symbol} Price: <span style='color:green; font-size:24px;'>${price}</span>",
                unsafe_allow_html=True)
                
                
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                break
    

    
    

                    
elif page =="News":
    API_KEY = "8d9da2b88c1a4a0c9992696407b51cdd"
    BASE_URL = "https://newsapi.org/v2/everything"

# Default Image 
    DEFAULT_IMAGE = "https://via.placeholder.com/300x200?text=No+Image"

# Streamlit App Title
    st.title("📰 Crypto News Tracker")

# User Coin Name Input 
    coin = st.text_input("🔍 Enter Coin Name:", "Bitcoin")

# API Data Fetch  Function
    def fetch_crypto_news(coin):
        params = {
        "q": coin,  # Coin Name
        "apiKey": API_KEY,  # API Key
        "language": "en",  # News Language (English)
        "sortBy": "publishedAt",  # Latest News First
    }
        response = requests.get(BASE_URL, params=params)
        data = response.json()
    
        if data.get("status") == "ok":
            return data["articles"][:5]  # Top 5 News
        return []

# Crypto News Data 
    news_articles = fetch_crypto_news(coin)

# News Show
    if news_articles:
       for news in news_articles:
           st.subheader(news["title"])
           st.image(news.get("urlToImage", DEFAULT_IMAGE), width=500)
           st.write(news["description"])
           st.write(f"[Read More]({news['url']})")
           st.write("---")
    else:
        st.write("⚠️ No news found. Try another coin name!")
        
        
elif page == "Chart":
    BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/!ticker@arr"

# Streamlit Title
    st.title("📊 Stable Live Crypto Market Dashboard ")
    table_placeholder = st.empty()
    top_gainers_chart = st.empty()
    top_losers_chart = st.empty()
    top_volume_chart = st.empty()
    candlestick_chart = st.empty()
    if "update_count" not in st.session_state:
        st.session_state.update_count = 0
    async def fetch_binance_data():
        async with websockets.connect(BINANCE_WS_URL) as ws:
            while True:
                data = json.loads(await ws.recv())
                df = pd.DataFrame(data)[["s", "c", "P", "h", "l", "v"]]
                df.columns = ["Symbol", "Last Price", "24h Change (%)", "High Price", "Low Price", "Volume"]
                df[["Last Price", "24h Change (%)", "High Price", "Low Price", "Volume"]] = df[
                ["Last Price", "24h Change (%)", "High Price", "Low Price", "Volume"]
            ].astype(float)

            # 📌 1️⃣ Update Stable Table
                table_placeholder.dataframe(df)

            # 📌 2️⃣ Top Gainers (Sorted by 24h % Change)
                top_gainers = df.sort_values(by="24h Change (%)", ascending=False).head(10)
                fig_gainers = go.Figure()
                fig_gainers.add_trace(go.Bar(
                x=top_gainers["Symbol"], 
                y=top_gainers["24h Change (%)"], 
                marker=dict(color=top_gainers["24h Change (%)"], colorscale="Greens")
            ))
                fig_gainers.update_layout(title="🚀 Top 10 Gainers", xaxis_title="Symbol", yaxis_title="24h Change (%)")

            # 📌 3️⃣ Top Losers (Sorted by 24h % Change)
                top_losers = df.sort_values(by="24h Change (%)", ascending=True).head(10)
                fig_losers = go.Figure()
                fig_losers.add_trace(go.Bar(
                x=top_losers["Symbol"], 
                y=top_losers["24h Change (%)"], 
                marker=dict(color=top_losers["24h Change (%)"], colorscale="Reds")
            ))
                fig_losers.update_layout(title="📉 Top 10 Losers", xaxis_title="Symbol", yaxis_title="24h Change (%)")

            # 📌 4️⃣ High Volume Coins
                high_volume = df.sort_values(by="Volume", ascending=False).head(10)
                fig_volume = go.Figure()
                fig_volume.add_trace(go.Bar(
                x=high_volume["Symbol"], 
                y=high_volume["Volume"], 
                marker=dict(color=high_volume["Volume"], colorscale="Blues")
            ))
                fig_volume.update_layout(title="🔊 Top 10 by Volume", xaxis_title="Symbol", yaxis_title="Volume")

            # 📌 5️⃣ Candlestick Chart (BTC/USDT)
                btc_data = df[df["Symbol"] == "BTCUSDT"]
                if not btc_data.empty:
                    fig_candle = go.Figure(data=[
                    go.Candlestick(
                        x=["Now"],  # Dummy time (WebSockets don't provide time)
                        open=[btc_data["Low Price"].values[0]], 
                        high=[btc_data["High Price"].values[0]], 
                        low=[btc_data["Low Price"].values[0]], 
                        close=[btc_data["Last Price"].values[0]]
                    )
                ])
                fig_candle.update_layout(title="📊 BTC/USDT Candlestick", xaxis_title="Time", yaxis_title="Price")

            # ✅ FIX: Stable Chart Updates (Unique Key)
                top_gainers_chart.plotly_chart(fig_gainers, use_container_width=True, key=f"gainers_chart_{st.session_state.update_count}")
                top_losers_chart.plotly_chart(fig_losers, use_container_width=True, key=f"losers_chart_{st.session_state.update_count}")
            
                top_volume_chart.plotly_chart(fig_volume, use_container_width=True, key=f"volume_chart_{st.session_state.update_count}")
                if not btc_data.empty:
                    candlestick_chart.plotly_chart(fig_candle, use_container_width=True, key=f"candlestick_chart_{st.session_state.update_count}")

            # 🔄 Increase Counter for Stable Charts
                    st.session_state.update_count += 1

                    await asyncio.sleep(1)  # Update every second
            # Run WebSocket Data Fetching
    async def main():
        await fetch_binance_data()

    asyncio.run(main())

if page == "About":
    
    st.subheader("🤔 Did You Know?")
    crypto_facts = [
    "Our dashboard updates live data every second using WebSockets!",
    "Binance API provides real-time market data for thousands of cryptocurrencies.",
    "Candlestick charts help traders analyze price movements effectively.",
    "High trading volume indicates strong market interest in a cryptocurrency.",
    "The crypto market operates 24/7, unlike traditional stock markets.",
    "Streamlit makes real-time data visualization easy with Plotly!"
]
    st.info(random.choice(crypto_facts))
    