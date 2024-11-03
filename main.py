import streamlit as st
from st_paywall import add_auth

add_auth(required=False)

if __name__ == '__main__':
    st.title("Charles AI")