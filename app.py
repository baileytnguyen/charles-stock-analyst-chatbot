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

# Function to get Google user info
def get_google_user_info(auth_code):
    token_url = "https://oauth2.googleapis.com/token"
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    token_data = {
        "code": auth_code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    if not access_token:
        st.error("Failed to retrieve access token.")
        return None
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    return user_info_response.json()

# Function to store user data
def store_user_data(email, data):
    supabase.table("user_data").insert({"email": email, "data": data}).execute()

# Check for auth code in query params
auth_code = st.query_params.get("code")
if auth_code:
    st.experimental_set_query_params()  # Clear query params
    user_info = get_google_user_info(auth_code[0])

    # Check if user info was successfully retrieved
    if user_info:
        email = user_info.get("email")
        st.session_state["user"] = email
        st.success(f"Welcome, {email}!")
    else:
        st.error("Failed to retrieve user information.")
        st.stop()  # Stop execution if user info fails to load

# Display content based on login state
if "user" in st.session_state:
    # Content for logged-in users
    st.header("User Dashboard")
    st.write("You are logged in successfully.")

    user_data = st.text_area("Enter some data:")
    if st.button("Submit"):
        store_user_data(st.session_state["user"], user_data)
        st.success("Data saved successfully!")
else:
    # Show Google login link if not logged in
    st.markdown(f"[Login with Google]({GOOGLE_AUTH_URL})")
