import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Streamlit app layout
st.title("Streamlit Supabase Google Authentication")

# State management for session
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

def login_with_google():
    """Function to log in a user using Google."""
    try:
        # Redirect to Google login
        url = supabase.auth.signInWithOAuth("google")
        st.write("Please log in using the following link:")
        st.markdown(f"[Login with Google]({url})")
    except Exception as e:
        st.error("Google login failed. Please try again.")

def logout_user():
    """Function to log out the current user."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.info("Logged out successfully.")

# Login with Google
if not st.session_state.authenticated:
    st.subheader("Login with Google")

    if st.button("Login with Google"):
        login_with_google()
else:
    st.success(f"Welcome, {st.session_state.user['email']}!")
    
    # Add additional content here for authenticated users
    st.write("You're logged in and can now access additional features.")

    # Logout button
    if st.button("Logout"):
        logout_user()
