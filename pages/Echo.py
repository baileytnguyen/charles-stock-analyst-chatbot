import streamlit as st
from dotenv import load_dotenv
import os
import time
import random
import requests
import mplfinance as mpf
import pandas as pd
from datetime import datetime
from openai import OpenAI

# Load environment variables
load_dotenv()

# Replace this with your actual Polygon.io and OpenAI API keys
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key from Streamlit secrets
openai_client = OpenAI(api_key=OPENAI_API_KEY)

st.title("Charles - Stock Charting Assistant")

# Helper function to stream a message with a delay
def stream_message(message, delay=0.05):
    for word in message.split():
        yield word + " "
        time.sleep(delay)

# Charles greeting emulator
def response_generator():
    response = random.choice(
        [
            "Hi, I'm Charles! How can I assist you in charting today?",
            "Charles here! Is there anything I can help chart for you?",
            "Hello! I'm Charles, your charting assistant. What can I chart for you today?",
        ]
    )
    return response

# Define functions to compute each indicator
def calculate_sma(data, period=14):
    return data['Close'].rolling(window=period).mean()

def calculate_ema(data, period=14):
    return data['Close'].ewm(span=period, adjust=False).mean()

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    return ema12 - ema26

def calculate_adx(data, period=14):
    high_diff = data['High'].diff()
    low_diff = data['Low'].diff()
    plus_dm = high_diff.where((high_diff > 0) & (high_diff > low_diff), 0)
    minus_dm = -low_diff.where((low_diff > 0) & (low_diff > high_diff), 0)
    atr = calculate_atr(data, period)
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    return dx.rolling(window=period).mean()

def calculate_atr(data, period=14):
    high_low = data['High'] - data['Low']
    high_close = (data['High'] - data['Close'].shift()).abs()
    low_close = (data['Low'] - data['Close'].shift()).abs()
    tr = high_low.combine(high_close, max).combine(low_close, max)
    return tr.rolling(window=period).mean()

def calculate_bollinger_bands(data, period=20):
    sma = data['Close'].rolling(window=period).mean()
    std = data['Close'].rolling(window=period).std()
    return sma + (2 * std), sma - (2 * std)

def calculate_obv(data):
    obv = (data['Volume'] * ((data['Close'] > data['Close'].shift()).astype(int) - 
                             (data['Close'] < data['Close'].shift()).astype(int))).cumsum()
    return obv

# Mapping of indicator names to calculation functions
indicator_functions = {
    "SMA": calculate_sma,
    "EMA": calculate_ema,
    "RSI": calculate_rsi,
    "MACD": calculate_macd,
    "ADX": calculate_adx,
    "ATR": calculate_atr,
    "Bollinger Bands": calculate_bollinger_bands,
    "OBV": calculate_obv,
}

# Configuration dictionary for each indicator's style
indicator_config = {
    "SMA": {"color": "blue", "style": "solid", "panel": 0},
    "EMA": {"color": "green", "style": "solid", "panel": 0},
    "RSI": {"color": "red", "style": "dashed", "panel": 1},
    "MACD": {"color": "purple", "style": "solid", "panel": 0},
    "ADX": {"color": "cyan", "style": "dotted", "panel": 1},
    "ATR": {"color": "magenta", "style": "dashed", "panel": 1},
    "Bollinger Bands": {"color": "purple", "style": "solid", "panel": 0, "bands": True},
    "OBV": {"color": "orange", "style": "solid", "panel": 1},
}

def plot_indicators(ticker, stock_data, indicators):
    
    # Clean the indicators list to remove empty strings
    indicators = [indicator for indicator in indicators if indicator.strip()]

    # Determine if volume or close price should be plotted based on indicators
    volume_requested = "Volume" in indicators
    price_requested = "Candlestick" in indicators or "Price" in indicators or not indicators  # Default to close price if no indicator

    # Plot the stock price as a standalone chart
    if price_requested:
        mpf_kwargs = {
            "type": "candle" if "Candlestick" in indicators else "line",
            "style": "charles",
            "title": f"{ticker} Stock Price",
            "ylabel": "Price (USD)",
            "volume": False,  # Volume handled separately
        }
        fig, ax = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
        st.pyplot(fig)

    # Plot each indicator as a separate standalone chart
    for indicator in indicators:
        
        if indicator in indicator_functions and indicator != "Volume":
            
            # Calculate the indicator values
            stock_data[indicator] = indicator_functions[indicator](stock_data)
            
            # Fetch specific configuration for this indicator
            config = indicator_config.get(indicator, {})
            color = config.get("color", "orange")
            linestyle = config.get("style", "solid")
            panel = config.get("panel", 1)
            
            # Special Case for Bollinger Bands
            if indicator == "Bollinger Bands":
                
                stock_data['BB_upper'], stock_data['BB_lower'] = stock_data[indicator]
                
                fig, ax = mpf.plot(
                    stock_data,
                    type="line",
                    style="charles",
                    title=f"{ticker} {indicator}",
                    addplot=[
                        mpf.make_addplot(stock_data['BB_upper'], panel=panel, color=color, linestyle="--", label=f"{indicator} Upper Band"),
                        mpf.make_addplot(stock_data['BB_lower'], panel=panel, color=color, linestyle="--", label=f"{indicator} Lower Band"),
                    ],
                    ylabel=indicator,
                    returnfig=True
                )
                
            # Calculate each indicator independently
            else:
                
                mpf_kwargs = {
    				"type": "line",         # Type of the main chart
    				"style": "charles",       # Chart style
    				"title": f"{ticker} {indicator}",
    				"ylabel": "Price (USD)",  # y-axis label for the main panel (stock price)
    				"addplot": [              # Add OBV as a separate indicator in its own panel
    					mpf.make_addplot(stock_data[indicator], panel=panel, color=color, linestyle=linestyle, ylabel=indicator)  # Separate panel with custom ylabel
    				],
    				"volume": False,          # Exclude volume from the main chart
    				"ylabel_lower": indicator,     # No y-label for lower volume, handled in addplot instead
    			}
    
    			# Plot the chart with two panels and distinct y-labels
                fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
    			
                # Display each indicator chart in Streamlit
                st.pyplot(fig)

    # Plot volume on its own chart if requested
    if volume_requested:
        mpf_kwargs = {
            "type": "line",
            "style": "charles",
            "title": f"{ticker} Volume",
            "volume": True,  # Display volume as a standalone chart
            "ylabel_lower": "Volume",
        }
        fig, ax = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
        st.pyplot(fig)

# Use OpenAI API to parse stock ticker and indicator/s from user input
def get_response(user_prompt):
    response = OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", 
             "content": """You are a helpful assistant that provides the stock ticker and only the requested indicators.
             When given input, respond in the following format:
             
             Ticker: <ticker>
             Indicators: <indicator1>, <indicator2>, ...

             If the user only provides a company name or ticker and does not specify indicators, respond with only the ticker and leave the Indicators field blank."""},
            {"role": "user", 
             "content": user_prompt},
        ],
        stream=False
    )
             
    # Convert response to dictionary if possible
    try:
        response_dict = response.to_dict()
    except AttributeError:
        # In case `.to_dict()` is not available, attempt accessing `choices` directly
        response_dict = response

    # Accessing choices
    if "choices" in response_dict and response_dict['choices']:
        content = response_dict['choices'][0]['message']['content']
        return content.strip()
    return ""
            
    

# Function to fetch stock data from Polygon API using URL
def fetch_stock_data(ticker, timespan="day", multiplier=1, limit=100, from_date="2024-01-01", to_date=None):
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")
    
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        f"?adjusted=true&sort=asc&limit={limit}&apiKey={POLYGON_API_KEY}"
    )
    
    response = requests.get(url)
    data = response.json()

    # Handle API response errors
    if response.status_code != 200 or "results" not in data:
        st.error("Error fetching stock data")
        return pd.DataFrame()

    return pd.DataFrame([
        {
            "Date": datetime.fromtimestamp(item["t"] / 1000),
            "Open": item["o"],
            "High": item["h"],
            "Low": item["l"],
            "Close": item["c"],
            "Volume": item["v"]
        }
        for item in data["results"]
    ]).set_index("Date")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial greeting if no other messages have been sent
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        response = response_generator()
        st.write_stream(stream_message(response))
        st.session_state.messages.append({"role": "assistant", "content": response})

# Accept user input
if prompt := st.chat_input("How can I help you?"):
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Initialize empty list to collect the assistant's response
    collected_messages = []
    ai_response = get_response(prompt)
    
    # Parse the ticker and indicators from the AI response
    ticker = None
    indicators = []

    if "Ticker:" in ai_response and "Indicators:" in ai_response:
        # Extract the ticker
        ticker = ai_response.split("Ticker:")[1].split("\n")[0].strip()
       
        # Extract the indicators as a list
        indicators = ai_response.split("Indicators:")[1].strip().split(", ")      

    else:
        st.error("Could not parse ticker and indicators from AI response.")


    # Example usage
    if ticker:
        # Fetch stock data using the parsed ticker
        stock_data = fetch_stock_data(ticker=ticker)
    
        if not stock_data.empty:
            # Assume indicators is a list of strings representing chosen indicators
            plot_indicators(ticker, stock_data, indicators)
        else:
            st.error("No data available for the specified ticker.")

