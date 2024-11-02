import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://friendlyuta-charles-app-register-login-authenticate-depl-grfpvj.streamlit.app/auth/v1/callback"  # Replace with your Streamlit app URL

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Google OAuth login URL
GOOGLE_AUTH_URL = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?client_id={GOOGLE_CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    "&response_type=code"
    "&scope=openid%20email%20profile"
)

st.title("Streamlit Google OAuth and Supabase Integration")

def get_google_user_info(auth_code):
    """Exchange code for token and retrieve user info from Google"""
    token_url = "https://oauth2.googleapis.com/token"
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"

    # Step 1: Exchange code for access token
    token_data = {
        "code": auth_code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    token_response = requests.post(token_url, data=token_data)
    
    # Debugging: Check token response
    st.write("Token response:", token_response.json())
    
    token_json = token_response.json()
    access_token = token_json.get("access_token")

    if not access_token:
        st.error("Failed to retrieve access token.")
        return None

    # Step 2: Retrieve user info
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    
    # Debugging: Check user info response
    st.write("User info response:", user_info_response.json())
    
    return user_info_response.json()

def store_user_data(email, data):
    """Store user data in Supabase"""
    response = supabase.table("user_data").insert({"email": email, "data": data}).execute()
    
    # Debugging: Check if data was stored successfully
    st.write("Supabase insert response:", response)

# Authentication flow
auth_code = st.query_params.get("code")
if auth_code:
    # Clear query params to avoid re-triggering
    st.experimental_set_query_params()
    
    # Debugging: Check if auth code is retrieved
    st.write("Auth code:", auth_code)

    # Retrieve user information using the auth code
    user_info = get_google_user_info(auth_code[0])
    
    # Debugging: Check if user info is retrieved
    st.write("User info:", user_info)
    
    if user_info:
        email = user_info["email"]
        st.session_state["user"] = email
        st.success(f"Welcome, {email}!")
        
        # User input section
        user_data = st.text_area("Enter some data:")
        
        if st.button("Submit"):
            
            # Debugging: Check if data is ready to be stored
            st.write("Storing data:", {"email": email, "data": user_data})
            
            store_user_data(email, user_data)
            st.success("Data saved successfully!")
else:
    st.markdown(f"[Login with Google]({GOOGLE_AUTH_URL})")
