import os
import re
import streamlit as st
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv
import time

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

# Function to validate email format
def is_valid_email(email: str) -> bool:
    email_regex = r"(^[\w\.-]+@[\w\.-]+\.\w{2,}$)"
    return re.match(email_regex, email) is not None

# Function to validate password complexity
def is_valid_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[0-9]", password):  # Ensure at least one digit
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Ensure at least one special character
        return False
    return True

# Registration Page
def registration_page():
    st.title("Register")
    
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        # Check if any field is empty
        if not (first_name and last_name and username and email and password and confirm_password):
            st.error("Please fill all fields.")
            return

        # Validate email format
        if not is_valid_email(email):
            st.error("Invalid email format.")
            return

        # Validate password complexity
        if not is_valid_password(password):
            st.error("Password must be at least 8 characters long, include at least one number and one special character.")
            return

        # Check if passwords match
        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        # Check if the email already exists
        existing_user = supabase.from_("User").select("email").eq("email", email).execute()
        if existing_user.data:
            st.error("Email already registered.")
            return

        # Hash the password
        hashed_password = hash_password(password)

        # Save the user information in Supabase
        user_data = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "username": username,
            "password": hashed_password,
            "isSubscribed": "false",
        }
        supabase.from_("User").insert(user_data).execute()
        
        st.success("Registration successful! Redirecting to login screen.")
        
        # Sleep 3 seconds before redirecting to login screen
        time.sleep(3)
        
        # Assuming "pages/login.py" is the path to your login page
        st.switch_page("pages/login.py")

# Run the app
registration_page()
