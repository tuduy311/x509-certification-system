import streamlit as st
import os

from views.auth import auth_page
from views.admin_dashboard import admin_dashboard
from views.user_dashboard import user_dashboard

from styles.theme import Global_CSS



Test_User = {
    "adimin" : {
        "password": "12345",
        "role": "admin"
    },

    "user": {
        "password" : "12345abc",
        "role" : "user"
    }
}

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = "Tu Duy"
if 'role' not in st.session_state:
    st.session_state.role = "user"
if 'access_token' not in st.session_state:
    st.session_state.access_token = None


# Streamlit set configuration
st.set_page_config(
    page_title = "X.509 Certificate System",
    page_icon = "🔐",
    layout= "wide"
)


st.markdown(Global_CSS, unsafe_allow_html= True)

def sidebar():
    with st.sidebar:

        st.write(f"User: {st.session_state.username}")
        st.write(f"Role: {st.session_state.role}")

        if st.sidebar.button("logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()

# ___________ Routing _____________________
if not st.session_state.authenticated:
    auth_page(Test_User)

else:
    sidebar()
    if st.session_state.role == "admin":
        admin_dashboard()

    elif st.session_state.role == "user":
        user_dashboard()