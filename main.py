import streamlit as st
import auth

if __name__ == '__main__':
    st.title("Streamlit OAuth Login")
    st.write(auth.get_login_str(), unsafe_allow_html=True)

    if st.button("Display User"):  
        auth.display_user()
