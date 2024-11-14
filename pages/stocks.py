import streamlit as st
import os
import time
import random
import indicators.plot as plot
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
    
    

# Initialize session state for storing the current ticker and indicators need for
# maintaining history since the OpenAI API does not store session history
if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = None
    
if "current_indicators" not in st.session_state:
    st.session_state.current_indicators = []
    


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
if (user_data["isTrial"] and user_data['trialRequestsLeft'] == 0):
    st.write("You have run out of free requests on your trial. Subscribe to continue using.")
    supabase.table("User").update({"trialEnded": True}).eq("email", st.session_state.email).execute()
    
elif (user_data["trialEnded"] and not user_data["isSubscribed"]):
    st.write("Subscribe to use Charles you are currently not subscribed")
    
else:

    # Accept user input
    if prompt := st.chat_input("How can I help you?"):
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
    
        # Get response and update indicators
        ticker, indicators = get_response(prompt)
        
        # Refresh the chart with the latest indicators
        plot.plot_current_indicators(ticker, indicators) 
        
        if (user_data["isTrial"]):
            supabase.table("User").update({"trialRequestsLeft": user_data["trialRequestsLeft"] - 1}).eq("email", st.session_state['email']).execute()
            user_data_response = supabase.from_("User").select("*").eq("email", st.session_state['email']).execute()
            if user_data_response.data and len(user_data_response.data) > 0:
                user_data = user_data_response.data[0]
                # Update the displayed requests remaining
                st.sidebar.write(f"Number of free requests remaining: {user_data['trialRequestsLeft']}")
