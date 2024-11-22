import requests
import os
import pandas as pd
import streamlit as st
from datetime import datetime


# Replace this with your actual Polygon.io key
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")


def fetch_financials(ticker):
    """
    Fetch financial data for a specific stock ticker from the Polygon API and display it.

    Parameters:
    - ticker (str): The stock ticker for which to fetch financial data.
    """
    
    # Construct URL for Polygon API request
    url = f"https://api.polygon.io/vX/reference/financials?ticker={ticker}&timeframe=quarterly&include_sources=false&apiKey={POLYGON_API_KEY}"
    
    # Make request to Polygon API
    try:
        response = requests.get(url)
        # Raise an error for unsuccessful status codes
        response.raise_for_status()  
        data = response.json()
        
    except requests.RequestException as e:
        st.error(f"Error fetching stock earnings: {e}")
        return []
    
    # Validate response content
    if "results" not in data or not data["results"]:
        st.error("No financial data found in the API response.")
        return
    
    financials = data["results"]
    
    return financials


# Function to fetch stock news
def fetch_stock_news(ticker):
    """
    Fetches the latest news for a specified stock ticker from the Polygon API.

    Parameters:
    - ticker (str): Stock ticker symbol.

    Returns:
    - list: A list of dictionaries with news details (title, date, summary, etc.).
    """
    # Construct URL for Polygon API request
    url = f"https://api.polygon.io/v2/reference/news?ticker={ticker}&apiKey={POLYGON_API_KEY}"

    # Make request to Polygon API
    try:
        response = requests.get(url)
        # Raise an error for unsuccessful status codes
        response.raise_for_status()  
        data = response.json()
        
    except requests.RequestException as e:
        st.error(f"Error fetching stock news: {e}")
        return []

    # Validate response content
    if "results" not in data:
        st.error("No news results found in the API response.")
        return []

    # Parse and return news data
    news_list = [{
        "Title": item.get("title"),
        "Published Date": item.get("published_utc"),
        "Description": item.get("description"),
        "Author": item.get("author"),
        "Source Name": item["publisher"].get("name") if "publisher" in item else None,
        "Source Logo URL": item["publisher"].get("logo_url") if "publisher" in item else None,
        "Article URL": item.get("article_url"),
        "Sentiment": item["insights"][0].get("sentiment") if item.get("insights") else None,
        "Sentiment Reasoning": item["insights"][0].get("sentiment_reasoning") if item.get("insights") else None
    } for item in data["results"]]
    
    return news_list


# Function to fetch stock data from Polygon API using URL
def fetch_stock_data(ticker, timespan="day", multiplier=1, limit=365, from_date="2024-01-01", to_date=None):
    """
    Fetches stock data for a specified ticker from the Polygon API within a date range.

    Parameters:
    - ticker (str): Stock ticker symbol.
    - timespan (str): Time unit for aggregation, e.g., "day", "minute". Default is "day".
    - multiplier (int): Multiplier for the timespan, e.g., 1 for daily data. Default is 1.
    - limit (int): Maximum number of results to fetch. Default is 100.
    - from_date (str): Start date for the data in "YYYY-MM-DD" format. Default is "2024-01-01".
    - to_date (str): End date for the data in "YYYY-MM-DD" format. Defaults to today's date if not provided.

    Returns:
    - pd.DataFrame: DataFrame with columns for "Open", "High", "Low", "Close", "Volume", and indexed by date.
      Returns an empty DataFrame if data retrieval fails or required columns are missing.
    """
    
    
    # Set default end date to today if not provided
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")
    
    # Construct URL for Polygon API request
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        f"?adjusted=true&sort=asc&limit={limit}&apiKey={POLYGON_API_KEY}"
    )
    
    # Make request to Polygon API
    try:
        response = requests.get(url)
        # Raise an error for unsuccessful status codes
        response.raise_for_status()  
        data = response.json()
        
    except requests.RequestException as e:
        st.error(f"Error fetching stock data: {e}")
        return pd.DataFrame()

    # Validate response content
    if "results" not in data:
        st.error("No results found in the API response.")
        return pd.DataFrame()

    # Parse data and construct DataFrame
    df = pd.DataFrame([{
        "Date": datetime.fromtimestamp(item["t"] / 1000),  # Convert timestamp to datetime
        "Open": item.get("o"),
        "High": item.get("h"),
        "Low": item.get("l"),
        "Close": item.get("c"),
        "Volume": item.get("v")
    } for item in data["results"]]).set_index("Date")

    # Required columns for plotting and analysis
    required_columns = ["Open", "High", "Low", "Close", "Volume"]

    # Validate presence of required columns
    if not all(col in df.columns for col in required_columns):
        st.error("Fetched data is missing required columns.")
        return pd.DataFrame()  # Return empty DataFrame if columns are missing

    return df