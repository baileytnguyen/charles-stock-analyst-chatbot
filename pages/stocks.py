import streamlit as st
import os
import time
import random
import re
import indicators.plot as plot
import polygon.data_fetcher as fetch
import polygon.display_news as display_news
import polygon.display_financials as display_financials
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv



# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Set OpenAI API key from Streamlit secrets
openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)


# Fetch user data from Supabase
user_data_response = supabase.from_("User").select("*").eq("email", st.session_state['email']).execute()

# Check if data retrieval was successful and data is present
if user_data_response.data and len(user_data_response.data) > 0:
    # Access the first item in the result list
    user_data = user_data_response.data[0]  
else:
    st.error("User data not found.")
    
    

# Initialize session state for storing the current ticker, indicators, timespan,
# news, and financials needed for maintaining history since the OpenAI API does not store session history
if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = None
    
if "current_indicators" not in st.session_state:
    st.session_state.current_indicators = []
	
if "current_timespan" not in st.session_state:
    st.session_state.current_timespan = "day"
    
if "current_news" not in st.session_state:
    st.session_state.current_news = "False"
    
if "current_financials" not in st.session_state:
    st.session_state.current_financials = "False"
    
available_timespans = ["hour", "day", "week", "month", "quarter", "year"]


# Page heading
st.title("Charles - Stock Charting Assistant")

# Display Navigation Links at the Top of the Page
st.sidebar.header("Navigation")
if st.sidebar.button("Home"):
    st.switch_page("pages/home.py")
    
# Check if the user is on a trial or not subscribed
if user_data["isTrial"] or not user_data["isSubscribed"]:
    if user_data["isTrial"]:
        st.sidebar.write("You are currently on a trial.")
    if st.sidebar.button("Subscribe for Full Access"):
        st.switch_page("pages/subscribeUser.py")       
        
# Display 'Logout' button
if st.sidebar.button("Logout"):
    # Reset logged-in state and redirect to login page
    st.session_state.logged_in = False
    st.switch_page("pages/login.py")  # The page name should match the configured TOML entry
    
# Add an expandable section for available indicators
with st.sidebar.expander("Available Indicators"):
    for indicator_name in plot.indicator_functions.keys():        
        st.write(indicator_name.upper())
        
# Add an expandable section for available indicators
with st.sidebar.expander("Available Timespans"):
    for timespan in available_timespans:        
        st.write(timespan.capitalize())

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
            
# Friendly response generator for updates
def generate_update_response(ticker=None, indicators=None, timespan=None, news=None, financials=None):
    """
    Generates a friendly response message based on the values that have actually changed.
    Combines messages for multiple updates to improve conversational flow.
    """
    changes = []

    # Detect changes and add to the changes list
    if ticker and ticker != st.session_state.current_ticker:
        changes.append(f"ticker to {ticker}")
    if indicators and sorted(indicators) != sorted(st.session_state.current_indicators):
        changes.append(f"indicators to {', '.join(indicators)}")
    if timespan and timespan != st.session_state.current_timespan:
        changes.append(f"timespan to {timespan}")
    if news is not None and news != st.session_state.current_news:
        if news == "True":
            changes.append("including the latest news")
        else:
            changes.append("removing news updates")
    if financials is not None and financials != st.session_state.current_financials:
        if financials == "True":
            changes.append("adding financial data")
        else:
            changes.append("skipping financial data")

    # Combine messages based on the number of changes
    if len(changes) == 1:
        response = f"Got it! Updating the {changes[0]}."
    elif len(changes) == 2:
        response = f"Absolutely! Updating the {changes[0]} and {changes[1]}."
    elif len(changes) > 2:
        response = f"All set! Updating the {', '.join(changes[:-1])}, and {changes[-1]}."
    else:
        response = "Nothing has changed."

    # If the user requested news and the ticker is provided, include that response
    if ticker and news == "True":
        response = f"Certainly, here is the news for {ticker}. {response}"

    # List of random closing statements
    closing_statements = [
        "Let me know how I can help!",
        "What else can I do for you?",
        "Feel free to ask if you need anything else.",
        "Happy to assist, let me know if you need more updates!",
        "Let me know if you'd like to make further changes."
    ]

    # Add a random closing statement to the response
    response += " " + random.choice(closing_statements)

    return response

# Use OpenAI API to parse stock ticker and indicator/s from user input
def get_response(user_prompt):
    """
    Uses the OpenAI API to parse a user’s input for stock-related information, including the ticker, indicators, timespan, news, and financials preference.
    Updates the session state with the parsed values.

    Parameters:
    - user_prompt (str): The user's input containing the stock request and any indicators.

    Returns:
    - tuple: (ticker, indicators, timespan, news, financials), where:
        - ticker (str): The stock ticker symbol.
        - indicators (list): A list of requested indicators.
        - timespan (str): The requested timespan (e.g., 'hour', 'day').
        - news (str): 'True', 'False', or None based on the user's preference for news updates.
        - financials (str): 'True', 'False', or None based on the user's preference for financials updates.
        - Returns (None, [], None, None) if parsing fails or no response is provided.
    """
    
    # Define the system prompt for OpenAI with current session state values
    system_prompt = f"""You are a helpful assistant that manages stock information based on user requests.
    The current ticker is '{st.session_state.current_ticker or "None"}'.
    The current indicators are: {", ".join(st.session_state.current_indicators) if st.session_state.current_indicators else "None"}.
    The current timespan is '{st.session_state.current_timespan}'.
    The current news is '{st.session_state.current_news}'.
    The current financials is '{st.session_state.current_financials}'.
    
    Your job:
    - Confirm the exact stock ticker symbol based on the user's input.
    - If a company name is provided, translate it to the correct ticker symbol.
    - When asked to add or remove an indicator, respond with an updated list of indicators as follows:
      - If adding, include only the new indicator(s) requested.
      - If removing, exclude only the specified indicator(s).
    - When asked to change the timespan, provide the new timespan only if it's part the supported timespan list which is "hour, day, week, month, quarter, year".
    - When asked to show or add news then return True. If asked to stop or remove news then return False. Otherwise, use the current news value to return
    - When asked to show or add financials then return True. If asked to stop or remove financials then return False. Otherwise, use the current financials value to return

    
    Response format:
    - Provide 'Ticker: <ticker>' and 'Indicators: <indicator1>, <indicator2>, ...' and 'Timespan: <timespan>' and 'News: <news>' and 'Financials: <financials>'.
    - If the ticker symbol or indicator list or timespan or news or financials does not change, keep the response consistent with the previous values.
    
    Strictly follow the above format, responding with the ticker and indicators and timeframe and news as specified, also providing a positive, friendly manner.
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
        return None, [], None, None, None


    # Parse response content to update ticker, indicators, timespan, news, and financials
    response_dict = response.to_dict() if hasattr(response, 'to_dict') else response
    
    # Ensure that response contains the expected structure
    if "choices" in response_dict and response_dict['choices']:
        content = response_dict['choices'][0].get('message', {}).get('content', "")

        if content:
            # Extract Ticker
            ticker_match = re.search(r"Ticker:\s*([^\n]+)", content)
            ticker = ticker_match.group(1).strip() if ticker_match else None

            # Extract Indicators
            indicators_match = re.search(r"Indicators:\s*([^\n]+)", content)
            indicators = (
                [ind.strip() for ind in indicators_match.group(1).split(",") if ind.strip()]
                if indicators_match else []
            )

            # Extract Timespan
            timespan_match = re.search(r"Timespan:\s*([^\n]+)", content)
            timespan = timespan_match.group(1).strip() if timespan_match else None

            # Extract News
            news_match = re.search(r"News:\s*(True|False)", content)
            news = news_match.group(1) if news_match else None
            
            # Extract Financials
            financials_match = re.search(r"Financials:\s*(True|False)", content)
            financials = financials_match.group(1) if news_match else None

            # Generate a friendly response
            update_message = generate_update_response(
                ticker=ticker,
                indicators=indicators,
                timespan=timespan,
                news=news,
                financials=financials,
            )
            
            # Update session state
            st.session_state.current_ticker = ticker
            st.session_state.current_indicators = indicators
            st.session_state.current_timespan = timespan
            st.session_state.current_news = news
            st.session_state.current_financials = financials

            # Display the response in the chat
            with st.chat_message("assistant"):
                st.write_stream(stream_message(update_message))
                st.session_state.messages.append({"role": "assistant", "content": update_message})

            st.success(f"Ticker: {ticker}, Indicators: {', '.join(indicators)}, Timespan: {timespan}, News: {news}, Financials: {financials}")
            return ticker, indicators, timespan, news, financials

        else:
            st.warning("Unexpected format in OpenAI response. Could not extract values.")

    # Return None and empty list if parsing fails
    return None, [], None, None, None

 

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

# If the user is on trial and there are no more free requests remaining prevent the user
# from being able to use charles
if ((user_data["isTrial"] and user_data['trialRequestsLeft'] > 0) or user_data["isSubscribed"]):

    # Accept user input
    if prompt := st.chat_input("How can I help you?"):
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
    
        # Get response and update indicators
        ticker, indicators, timespan, news, financials = get_response(prompt)
        
        # Get news for the given stock if requested
        if (news == "True"):             
            # Fetch the stock news from polygon
            news_data = fetch.fetch_stock_news(ticker)
            # Display the news in streamlit
            display_news.display_stock_news(news_data, ticker)
            
        # Get financials for the given stock if requested
        if (financials == "True"):
            # Fetch the stock financials from polygon
            financials_data = fetch.fetch_financials(ticker)
            # Display the financials in streamlit
            display_financials.display_financial_statements(financials_data, ticker)            
        
        # Refresh the chart with the latest indicators
        plot.plot_current_indicators(ticker, indicators, timespan) 
        
        if (user_data["isTrial"]):
            supabase.table("User").update({"trialRequestsLeft": user_data["trialRequestsLeft"] - 1}).eq("email", st.session_state['email']).execute()
            user_data_response = supabase.from_("User").select("*").eq("email", st.session_state['email']).execute()
            if user_data_response.data and len(user_data_response.data) > 0:
                user_data = user_data_response.data[0]
                # Update the displayed requests remaining
                st.sidebar.write(f"Number of free requests remaining: {user_data['trialRequestsLeft']}")
else:
    st.write("Subscribe to use Charles you are currently not subscribed")
    