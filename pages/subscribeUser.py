import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import re
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
st.title(f"Welcome, {username}!")
st.write("Please fill out the information below to subscribe to Charles.")

# Subscription form
st.write("### Subscription Payment Details")

# Credit card details form
credit_card_number = st.text_input("Credit Card Number")
expiration_date = st.text_input("Expiration Date (MM/YY)")
cvv = st.text_input("CVV", type="password")
zip_code = st.text_input("Zip Code")

# Auto-renew checkbox
auto_renew = st.checkbox("Auto-Renew Subscription")

# Function to validate the input fields
def validate_input(cc_number, exp_date, cvv, zip_code):
    # Check if credit card number is numeric and 16 digits long
    if not re.match(r"^\d{16}$", cc_number):
        return "Credit Card Number must be 16 digits long and numeric."
    
    # Check if expiration date is in the correct format
    if not re.match(r"^(0[1-9]|1[0-2])/[0-9]{2}$", exp_date):
        return "Expiration Date must be in MM/YY format."
    
    # Check if CVV is numeric and 3 digits long
    if not re.match(r"^\d{3}$", cvv):
        return "CVV must be 3 digits long and numeric."
    
    # Check if zip code is numeric and 5 digits long
    if not re.match(r"^\d{5}$", zip_code):
        return "Zip Code must be 5 digits long and numeric."
    
    return None  # No errors

# Subscribe button for form submission
if st.button("Confirm Subscription"):
    # Validate inputs
    error_message = validate_input(credit_card_number, expiration_date, cvv, zip_code)
    
    if error_message:
        st.error(error_message)  # Display error message
    else:
        # Here you would add the logic to process the payment
        
        response = (supabase.table("User").update({"isSubscribed": True}).eq("email", st.session_state.email).execute())
        st.success("Subscription successful! Redirecting to the Home Screen!")
        # Sleep 3 seconds before redirecting to login screen
        time.sleep(3)
        st.switch_page("pages/stocks.py")



