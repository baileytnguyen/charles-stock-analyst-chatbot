import os
import streamlit as st
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Helper function to hash passwords
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Helper function to check password
def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# Login Page
def login_page():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = supabase.from_("User").select("password").eq("email", email).execute()

        if user.data:
            stored_password = user.data[0]["password"]
            if check_password(password, stored_password):
                st.success("Login successful!")
                st.session_state.logged_in = True
                st.session_state.email = email
                isSubscribed = supabase.from_("User").select("isSubscribed").eq("email", st.session_state.email).execute()
                if (isSubscribed.data[0]["isSubscribed"]):
                    st.switch_page("pages/stocks.py")
                else :
                    st.switch_page("pages/subscribe.py")
            else:
                st.error("Incorrect Credentials.")
        else:
            st.error("Incorrect Credentials.")
    st.text("Need an account?")

    if st.button("Register"):
        st.switch_page("pages/register.py")

# Run the app
login_page()