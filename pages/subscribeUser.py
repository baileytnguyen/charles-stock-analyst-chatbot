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



def start_trial(email):
    # Set trial status and trial request count
    trial_data = {
        "isTrial": True,
        "trialRequestsLeft": 3  # Initial trial request limit
    }
    
    # Update user in Supabase
    response = supabase.table("User").update(trial_data).eq("email", st.session_state['email']).execute()
    return response

def end_trial(email):
    # Set trial status and trial request count
    trial_data = {
        "isTrial": False,
        "trialRequestsLeft": 0
    }
    
    # Update user in Supabase
    response = supabase.table("User").update(trial_data).eq("email", st.session_state['email']).execute()
    return response


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



# Fetch user data from Supabase
user_data_response = supabase.from_("User").select("*").eq("email", st.session_state['email']).execute()

# Check if data retrieval was successful and data is present
if user_data_response.data and len(user_data_response.data) > 0:
    # Access the first item in the result list
    user_data = user_data_response.data[0]  
else:
    st.error("User data not found.")
    
    
    

# Welcome message
st.title(f"Welcome, {user_data['username']}!")
st.write("Please fill out the information below to subscribe to Charles.")

# Redirect non-subscribers to subscription page
if not user_data["isSubscribed"]:  
    
    if user_data["isTrial"]:        
        # Trial user - display remaining requests and continue option
        st.title("Trial Access")
        st.write(f"You have {user_data['trialRequestsLeft']} requests remaining in your trial.")    
        
        if st.button("Continue Trial"):     
            
            if user_data['trialRequestsLeft'] > 0:               
                st.success("Trial request accepted! Redirecting to the Stocks page.")
                time.sleep(2)
                st.switch_page("pages/stocks.py")           
            else:               
                st.error("Your trial has expired. Please subscribe to continue using the service.")
                
    # Only display the ability to start a trial if the user has not started one
    elif not user_data["trialEnded"]:
        # Offer to start a trial for a non-subscribing user without an active trial
        st.title("Start a Free Trial")
        
        if st.button("Start Trial"):
            response = start_trial(st.session_state['email'])
            
            if response:
                st.success("Trial started! You have 3 requests remaining. Redirecting to the Stocks page.")
                time.sleep(2)
                st.switch_page("pages/stocks.py")
                
            else: 
                st.error("Error starting trial. Please try again later.")

# Subscription form
st.write("### Subscription Payment Details")

# Credit card details form
credit_card_number = st.text_input("Credit Card Number")
expiration_date = st.text_input("Expiration Date (MM/YY)")
cvv = st.text_input("CVV", type="password")
zip_code = st.text_input("Zip Code")

# Auto-renew checkbox
auto_renew = st.checkbox("Auto-Renew Subscription")


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
        end_trial(st.session_state['email'])
        # Sleep 3 seconds before redirecting to home screen
        time.sleep(3)
        st.switch_page("pages/home.py")



