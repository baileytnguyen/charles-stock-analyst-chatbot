# IMPORTING LIBRARIES
import os
import streamlit as st
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")

# Initialize the Google OAuth2 client
client = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)

async def get_authorization_url():
    return await client.get_authorization_url(REDIRECT_URL, scope=["profile", "email"])

async def get_access_token(code: str):
    return await client.get_access_token(code, REDIRECT_URL)

async def get_user_email(token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email

def get_login_str():
    # Generate the Google login link
    authorization_url = asyncio.run(get_authorization_url())
    return f'<a target="_self" href="{authorization_url}">Google Login</a>'

def display_user():
    # Attempt to retrieve 'code' from the query parameters
    query_params = st.experimental_get_query_params()
    code = query_params.get('code')
    
    if code:
        # Fetch access token and user email if code is present
        token = asyncio.run(get_access_token(code[0]))
        user_id, user_email = asyncio.run(get_user_email(token['access_token']))
        st.write(f"You're logged in as {user_email}, with user ID: {user_id}")
    else:
        st.write("Authorization code not found in URL. Please log in first.")
