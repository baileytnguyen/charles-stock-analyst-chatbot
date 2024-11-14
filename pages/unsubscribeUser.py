import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# Fetch Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Fetch user data from Supabase
user_data_response = supabase.from_("User").select("*").eq("email", st.session_state['email']).execute()

# Check if data retrieval was successful and data is present
if user_data_response.data and len(user_data_response.data) > 0:
    # Access the first item in the result list
    user_data = user_data_response.data[0]  
else:
    st.error("User data not found.")



# Set page configuration
st.set_page_config(page_title="Charles Homepage", page_icon="💳", layout="centered")



# Welcome message
st.title(f"Goodbye, {user_data['username']}!")
st.write("You are about to unsubscribe from Charles.")

# Confirmation prompt
st.write("Are you sure you want to unsubscribe? This will cancel your subscription.")

# Confirmation checkbox
confirm_unsubscribe = st.checkbox("Yes, I want to unsubscribe")

# Unsubscribe action if confirmed
if confirm_unsubscribe:
    if st.button("Confirm Unsubscribe"):
        # Update subscription status to False in the database
        response = supabase.table("User").update({"isSubscribed": False}).eq("email", st.session_state.email).execute()
        
        if response: 
            st.success("You have successfully unsubscribed. We hope to see you again!")
            time.sleep(2)  # Optional: Delay before redirecting
            st.session_state.is_trial = True  # Re-enable trial mode
            st.session_state.trial_counter = 0  # Reset trial counter
            st.switch_page("pages/home.py")  # Redirect to home or a specific page after unsubscribing
        else:
            st.error("There was an error while processing your unsubscribe request. Please try again later.")
    
    st.write("You can re-subscribe anytime!")
else:
    st.write("You have not confirmed your unsubscribe request. If you change your mind, you can always come back and manage your subscription.")
