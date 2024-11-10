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

# Set page configuration
st.set_page_config(page_title="Charles Homepage", page_icon="💳", layout="centered")

def get_username(user_id):
    # Query the database to retrieve the name column based on user_id
    response = supabase.table("user_data").select("first_name").eq("id", user_id).execute()
    if response.data:
        return response.data[0]["first_name"].strip()
    return "User"

# Fetch username (replace 'user_id' with actual logged-in user's ID)
user_id = 1  # Example user ID; replace this with the actual user ID after login
username = get_username(user_id)

# Welcome message
st.title(f"Goodbye, {username}!")
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
            st.switch_page("pages/login.py")  # Redirect to home or a specific page after unsubscribing
        else:
            st.error("There was an error while processing your unsubscribe request. Please try again later.")
    
    st.write("You can re-subscribe anytime!")
else:
    st.write("You have not confirmed your unsubscribe request. If you change your mind, you can always come back and manage your subscription.")
