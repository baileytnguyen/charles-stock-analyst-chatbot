import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import openai  # Import OpenAI library

load_dotenv()

# Replace this with your actual Polygon.io and OpenAI API keys
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

def fetch_stock_data(ticker):
    start_date = "2023-11-01"  # Start of the desired timespan
    end_date = "2023-11-30"     # End of the desired timespan
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?adjusted=true&apiKey={POLYGON_API_KEY}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        # Check if the 'results' field contains data points
        if 'results' in data:
            stock_data = pd.DataFrame(data['results'])
            stock_data['date'] = pd.to_datetime(stock_data['t'], unit='ms')  # Convert timestamp to date
            return stock_data[['date', 'c']]  # Returning only date and close price columns
        else:
            st.error("No data found for this ticker.")
            return None
    else:
        st.error("Error fetching data. Please check the stock symbol and try again.")
        return None

def get_ticker_from_chatbot(user_input):
    # Create a prompt for the chatbot to identify the ticker symbol
    prompt = f"Provide only the stock ticker for the given input and only give the ticker. Nothing else: '{user_input}'."

    # Call OpenAI API to get the response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract the message content from the response
    if response.choices:
        return response.choices[0].message['content'].strip()
    return None

# Streamlit App
st.title("Stock Chart Viewer")

stock_name = st.text_input("Enter Stock Name", "Apple")

if st.button("Fetch Ticker and Data"):
    ticker = get_ticker_from_chatbot(stock_name)
    if ticker:
        st.write(f"Fetching data for ticker: {ticker}")

        stock_data = fetch_stock_data(ticker.upper())
        if stock_data is not None:
            st.write(f"Displaying data for {ticker.upper()}")

            # Display a line chart
            fig, ax = plt.subplots()
            ax.plot(stock_data['date'], stock_data['c'], label="Close Price")
            ax.set_title(f"{ticker.upper()} Stock Price")
            ax.set_xlabel("Date")
            ax.set_ylabel("Close Price (USD)")
            ax.legend()

            # Rotate x-axis labels and adjust layout
            plt.xticks(rotation=45)
            plt.tight_layout()

            st.pyplot(fig)
    else:
        st.error("Could not retrieve ticker symbol from the chatbot.")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.switch_page("pages/login.py")