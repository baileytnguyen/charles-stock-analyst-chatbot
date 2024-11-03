import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

def get_username(email):
    # Query the database to retrieve the name column based on user_id
    response = supabase.table("User").select("username").eq("email", email).execute()
    if response.data:
        return response.data[0]["username"]
    return "User"

def home_page():
    if (st.session_state.logged_in == True):
        username = get_username(st.session_state.email)
        st.title(f"Welcome, {username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.switch_page("pages/login.py")
    else:
        st.error("User Not Authenticated.")
# Run the app
home_page()
