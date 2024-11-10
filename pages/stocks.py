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

# Import indicator calculation functions
import indicators.calculations as calc


# Load environment variables
load_dotenv()

# Replace this with your actual Polygon.io and OpenAI API keys
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key from Streamlit secrets
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize session state for storing the current ticker and indicators need for
# maintaining history since the OpenAI API does not store session history
if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = None
    
if "current_indicators" not in st.session_state:
    st.session_state.current_indicators = []
    
# Mapping of indicator names to calculation functions
indicator_functions = {
    "SMA": calc.calculate_sma,
    "EMA": calc.calculate_ema,
    "RSI": calc.calculate_rsi,
    "MACD": calc.calculate_macd,
    "ADX": calc.calculate_adx,
    "ATR": calc.calculate_atr,
    "Bollinger Bands": calc.calculate_bollinger_bands,
    "OBV": calc.calculate_obv,
    "DMI": calc.calculate_dmi,
    "Parabolic SAR": calc.calculate_parabolic_sar,
    "VROC": calc.calculate_vroc,
}

# Configuration dictionary for each indicator's style
indicator_config = {
    "SMA": {"color": "blue", "style": "solid", "panel": 0},
    "EMA": {"color": "green", "style": "solid", "panel": 0},
    "RSI": {"color": "red", "style": "dashed", "panel": 1},
    "MACD": {"color": "purple", "style": "solid", "panel": 1},
    "ADX": {"color": "cyan", "style": "dotted", "panel": 1},
    "ATR": {"color": "magenta", "style": "dashed", "panel": 1},
    "Bollinger Bands": {"color": "purple", "style": "solid", "panel": 0, "bands": True},
    "OBV": {"color": "orange", "style": "solid", "panel": 1},
    "DMI": {"color": "blue", "style": "dashed", "panel": 1},
    "Parabolic SAR": {"color": "green", "style": "solid", "panel": 1},
    "VROC": {"color": "orange", "style": "solid", "panel": 1},
}

# Page heading
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


def plot_current_indicators():
    """
    Fetches the latest stock data for the current ticker and plots the indicators requested by the user.
    
    Parameters:
    - None. This function relies on Streamlit session state variables for the current ticker and indicators.

    Functionality:
    - Checks for the current ticker and indicators in session state.
    - Fetches stock data for the specified ticker.
    - Displays an error if no ticker or data is available.
    - Calls plot_indicators to visualize the ticker data and selected indicators.
    """
    
    # Retrieve the current ticker and indicators from session state
    ticker = st.session_state.current_ticker
    indicators = st.session_state.current_indicators

    # Check if a ticker is set in session state
    if ticker:
        
        # Fetch stock data for the specified ticker
        stock_data = fetch_stock_data(ticker)
        
        # Check if fetched data is empty, indicating an issue with data retrieval
        if stock_data.empty:
            st.error("No data available for the specified ticker.")
            
        else:
            # Plot the indicators on the fetched stock data
            plot_indicators(ticker, stock_data, indicators)
            
    else:
        # Display an error if no ticker is set
        st.error("No ticker or indicators to display.")



def plot_indicators(ticker, stock_data, indicators):
    """
    Plots the main stock price and specified technical indicators for the given ticker symbol.
    
    Parameters:
    - ticker: str, the stock ticker symbol
    - stock_data: DataFrame, containing the stock's OHLC and volume data
    - indicators: list of str, the names of the indicators to plot
    
    Returns:
    - None, displays plots using Streamlit
    """
    
    # Remove any empty strings from the indicators list
    indicators = [indicator for indicator in indicators if indicator.strip()]

    # Determine whether to plot volume or close price based on indicators
    volume_requested = "Volume" in indicators
    price_requested = "Candlestick" in indicators or "Price" in indicators or not indicators  # Default to close price if no indicator

    # Plot the main stock price chart
    if price_requested:
        
        mpf_kwargs = {
            "type": "candle" if "Candlestick" in indicators else "line",
            "style": "charles",
            "title": f"{ticker} Stock Price",
            "ylabel": "Price (USD)",
            "volume": False,  # Volume will be plotted separately if requested
        }
        fig, ax = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
        st.pyplot(fig)
        

    # Loop through indicators to plot each as a separate chart
    for indicator in indicators:
        
        # Ensure the indicator is defined in the functions and skip Volume
        if indicator in indicator_functions and indicator != "Volume":
            
            try:
                # Calculate the indicator values
                indicator_values = indicator_functions[indicator](stock_data)
                
                # Get the specific plot configuration for this indicator
                config = indicator_config.get(indicator, {})
                color = config.get("color", "orange")
                linestyle = config.get("style", "solid")
                panel = config.get("panel", 1)
                
                # Special handling for Bollinger Bands, which has upper and lower bands
                if indicator == "Bollinger Bands":
                    
                    if isinstance(indicator_values, tuple) and len(indicator_values) == 2:
                        stock_data['BB_upper'], stock_data['BB_lower'] = indicator_values
                        
                    else:
                        st.warning(f"Invalid Bollinger Bands data for {ticker}. Skipping plot.")
                        continue
                    
                    mpf_kwargs = {
        				"type": "line",
        				"style": "charles",
        				"title": f"{ticker} {indicator}",
        				"ylabel": "Price (USD)",
        				"addplot": [
                            mpf.make_addplot(stock_data['BB_upper'], panel=panel, color=color, linestyle="--", label=f"{indicator} Upper Band"),
                            mpf.make_addplot(stock_data['BB_lower'], panel=panel, color=color, linestyle="--", label=f"{indicator} Lower Band"),
        				],
        				"volume": False,          # Exclude volume from the main chart
        			}
                    
                    
                # Special handling for MACD, requires the histogram, signal line and MACD line
                elif indicator == "MACD":
                    
                    # Calculate the MACD components
                    macd_line, signal_line, histogram = calc.calculate_macd(stock_data)
                    
                    # Check if MACD calculation succeeded
                    if macd_line is not None and signal_line is not None and histogram is not None:
                        # Add the three components to the plot
                        mpf_kwargs = {
                            "type": "line",
                            "style": "charles",
                            "title": f"{ticker} {indicator}",
                            "ylabel": "Price (USD)",
                            "addplot": [
                                mpf.make_addplot(macd_line, panel=panel, color="blue", label="MACD Line", secondary_y=False),
                                mpf.make_addplot(signal_line, panel=panel, color="red", label="Signal Line", secondary_y=False),
                                mpf.make_addplot(histogram, panel=panel, type="bar", color="grey", label="Histogram", secondary_y=False)
                            ],
                            "volume": False,
                        }                       
                        
                    else:
                        st.warning("MACD components could not be calculated for the plot.")
                        
                        
                # Plotting Parabolic SAR Indicator
                elif indicator == "Parabolic SAR":
                    
                    # Calculate the Parabolic SAR values for the stock data
                    sar = calc.calculate_parabolic_sar(stock_data)
                    
                    mpf_kwargs = {
                        "type": "line",
                        "style": "charles",
                        "title": f"{ticker} {indicator}",
                        "ylabel": "Price (USD)",
                        "addplot": [
                            mpf.make_addplot(sar, type='scatter', markersize=5, marker='.', color='red'),
                        ],
                        "volume": False,
                    }
                        
                    
                # Plotting Directional Movement Index (DMI) Indicator
                elif indicator == "DMI":
                    
                    # Calculate +DI and -DI values for Directional Movement Index
                    plus_di, minus_di = calc.calculate_dmi(stock_data)
                    
                    mpf_kwargs = {
                        "type": "line",
                        "style": "charles",
                        "title": f"{ticker} DMI (+DI / -DI)",
                        "addplot": [
                            mpf.make_addplot(plus_di, panel=config["panel"], color=config["color"], label="+DI"),
                            mpf.make_addplot(minus_di, panel=config["panel"], color="red", label="-DI"),
                        ]
                    }

                    
                # Handle all other individual indicators that are plotted independently
                else:
                    
                    # Assign the calculated indicator values to a DataFrame column if they match the data length
                    if len(indicator_values) == len(stock_data):
                        stock_data[indicator] = indicator_values
                        
                    else:
                        st.warning(f"{indicator} calculation mismatch for {ticker}. Skipping plot.")
                        continue
                    
                    mpf_kwargs = {
        				"type": "line",  
        				"style": "charles",
        				"title": f"{ticker} {indicator}",
        				"ylabel": "Price (USD)",
        				"addplot": [
        					mpf.make_addplot(stock_data[indicator], panel=panel, color=color, linestyle=linestyle, label=f"{indicator}", ylabel=indicator)  # Separate panel with custom ylabel
        				],
        				"volume": False,
        			}
        
     			# Plot the indicator chart
                fig, axlist = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
                st.pyplot(fig)
                    
            except Exception as e:
                st.error(f"Error plotting {indicator} for {ticker}: {e}")
                continue

    # Plot volume chart as a standalone panel if requested
    if volume_requested:
        
        try: 
            mpf_kwargs = {
                "type": "line",
                "style": "charles",
                "title": f"{ticker} Volume",
                "volume": True,  # Display volume as a standalone chart
                "ylabel_lower": "Volume",
            }
            fig, ax = mpf.plot(stock_data, **mpf_kwargs, returnfig=True)
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error plotting volume for {ticker}: {e}")
            

# Use OpenAI API to parse stock ticker and indicator/s from user input
def get_response(user_prompt):
    """
    Uses the OpenAI API to parse a user’s input for a stock ticker and requested indicators.
    Updates session state with the parsed ticker and indicators.
    
    Parameters:
    - user_prompt (str): The user's input containing the stock request and any indicators.
    
    Returns:
    - tuple: (ticker, indicators), where:
        - ticker (str): The stock ticker symbol.
        - indicators (list): A list of requested indicators.
        - Returns (None, []) if parsing fails or no response is provided.
    """
    
    # Define the system prompt for OpenAI with current session state values
    system_prompt = f"""You are a helpful assistant that manages stock information based on user requests.
    The current ticker is '{st.session_state.current_ticker or "None"}'.
    The current indicators are: {", ".join(st.session_state.current_indicators) if st.session_state.current_indicators else "None"}.
    
    Your job:
    - Confirm the exact stock ticker symbol based on the user's input.
    - If a company name is provided, translate it to the correct ticker symbol.
    - When asked to add or remove an indicator, respond with an updated list of indicators as follows:
      - If adding, include only the new indicator(s) requested.
      - If removing, exclude only the specified indicator(s).
    
    Response format:
    - Only provide 'Ticker: <ticker>' and 'Indicators: <indicator1>, <indicator2>, ...'.
    - If the ticker symbol or indicator list does not change, keep the response consistent with the previous values.
    
    Strictly follow the above format, responding only with the ticker and indicators as specified, and no additional text or explanations.
    """


    try:
        # Call OpenAI API to process user request
        response = OpenAI().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False
        )
        
    except Exception as e:
        st.error(f"Error communicating with OpenAI API: {e}")
        return None, []


    # Parse response content to update ticker and indicators
    response_dict = response.to_dict() if hasattr(response, 'to_dict') else response
    
    # Ensure that response contains the expected structure
    if "choices" in response_dict and response_dict['choices']:
        
        content = response_dict['choices'][0].get('message', {}).get('content', "")

        # Check for both 'Ticker' and 'Indicators' in the response to validate format
        if "Ticker:" in content and "Indicators:" in content:
            
            # Extract and clean up the ticker
            ticker = content.split("Ticker:")[1].split("\n")[0].strip()
            
            # Extract and clean up the indicators, ensuring no empty strings
            indicators = [ind.strip() for ind in content.split("Indicators:")[1].strip().split(",") if ind.strip()]

            # Update session state with the new ticker and indicators
            st.session_state.current_ticker = ticker
            st.session_state.current_indicators = indicators

            return ticker, indicators

        else:
            st.warning("Unexpected format in OpenAI response. Could not extract ticker and indicators.")
    
    # Return None and empty list if parsing fails
    return None, []
            
    

# Function to fetch stock data from Polygon API using URL
def fetch_stock_data(ticker, timespan="day", multiplier=1, limit=100, from_date="2024-01-01", to_date=None):
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

    # Get response and update indicators
    ticker, indicators = get_response(prompt)
    
    # Refresh the chart with the latest indicators
    plot_current_indicators() 

