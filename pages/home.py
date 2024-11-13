import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Display Navigation Links at the Top of the Page
st.sidebar.header("Navigation")
if st.sidebar.button("Stocks"):
    st.switch_page("pages/stocks.py")

def get_username(email):
    """
    Retrieves the username associated with a given email from the database.

    Parameters:
    - email (str): The email address of the user.

    Returns:
    - str: The username associated with the email if found, or "User" as a fallback.
    """
    
    try:
        # Query the "User" table in the database for the username corresponding to the provided email
        response = supabase.table("User").select("username").eq("email", email).execute()
        
        # Check if response contains data, and return the username if available
        if response.data and "username" in response.data[0]:
            return response.data[0]["username"]
        
    except Exception as e:
        # Log the error and return a default username if an error occurs
        st.error("Error retrieving username from the database.")
        st.error(f"Details: {e}")
    
    # Fallback return value if no username is found or an error occurs
    return "User"


def home_page():
    """
    Displays the home page for the logged-in user, showing their username,
    subscription status, and options to unsubscribe or logout.
    """
    
    # Check if user is logged in
    if st.session_state.logged_in:
        # Retrieve and display the username based on the user's email
        username = get_username(st.session_state.email)
        st.title(f"Welcome, {username}")

        # Retrieve subscription status from the database
        try:
            subscription_status = supabase.from_("User").select("isSubscribed").eq("email", st.session_state.email).execute()
            is_subscribed = subscription_status.data[0]["isSubscribed"]
            
            # Display 'Unsubscribe' button if the user is subscribed
            if is_subscribed:
                if st.button("Unsubscribe"):
                    # Redirect to the unsubscribe page if clicked
                    st.switch_page("pages/unsubscribeUser.py")  # The page name should match the configured TOML entry
       
        except Exception as e:
            # Display an error if there was an issue fetching subscription status
            st.error("Error fetching subscription status.")
            st.error(f"Details: {e}")

        # Display 'Logout' button
        if st.button("Logout"):
            # Reset logged-in state and redirect to login page
            st.session_state.logged_in = False
            st.switch_page("pages/login.py")  # The page name should match the configured TOML entry
    
    else:
        # Display error if user is not authenticated
        st.error("User not authenticated.")
        
# Run the app
home_page()
