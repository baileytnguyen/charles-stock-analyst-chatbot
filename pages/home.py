import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)


# Fetch user data from Supabase
user_data_response = supabase.from_("User").select("*").eq("email", st.session_state['email']).execute()

# Check if data retrieval was successful and data is present
if user_data_response.data and len(user_data_response.data) > 0:
    # Access the first item in the result list
    user_data = user_data_response.data[0]  
else:
    st.error("User data not found.")



# Display Navigation Links at the Top of the Page
st.sidebar.header("Navigation")
if st.sidebar.button("Stocks"):
    st.switch_page("pages/stocks.py")
    
# Check if the user is on a trial
if user_data["isTrial"] or not user_data["isSubscribed"]:
    if st.sidebar.button("Subscribe"):
        # Display the link to subscribe if the user is on a trial
        st.switch_page("pages/subscribeUser.py")
        
# Check if the user is on a trial
if user_data["isSubscribed"]:
    if st.sidebar.button("Unsubscribe"):
        # Display the link to subscribe if the user is on a trial
        st.switch_page("pages/unsubscribeUser.py")

# Display 'Logout' button
if st.sidebar.button("Logout"):
    # Reset logged-in state and redirect to login page
    st.session_state.logged_in = False
    st.switch_page("pages/login.py")  # The page name should match the configured TOML entry

def home_page():
    """
    Displays the home page for the logged-in user, showing their username, and
    subscription status
    """
    
    # Check if user is logged in
    if st.session_state.logged_in:
        
        # Retrieve and display the username based on the user's email
        username = user_data["username"]
        st.title(f"Welcome, {username}")
        
        if user_data["isSubscribed"]:
            st.write("Thank you for being a valued subscriber")
        else:
            st.write("To gain full access to Charles please consider subscribing your future depends on it")
 
    else:
        # Display error if user is not authenticated
        st.error("User not authenticated.")
        
# Run the app
home_page()
