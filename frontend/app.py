import streamlit as st
import os

from views.auth import auth_page
from views.admin_dashboard import admin_dashboard
from views.user_dashboard import user_dashboard



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
    st.session_state.authenticated = True
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
    layout = "centered" if not st.session_state.authenticated else "wide"
)


st.markdown( """   
<style>
    .stApp {
      #  background: linear-gradient(135deg, #0B1020 0%, #0F172A 50%, #1a1f3a 100%) !important;
        background : rgb(21, 33, 51) !important;

        background-attachment: fixed !important;
    }
            
    /* ── Remove default block padding ── */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
        margin: auto !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgb(7, 18, 50, 0.8) !important;
        backdrop-filter: blur(10px) !important;
      
    }

    /* Sidebar text */
    [data-testid="stSidebar"] > div > div > div {
        color: #CBD5E1 !important;
    }
            

    /* Main content */
    .main {
        background: transparent !important;
    }

    span, div, label {
        #color: #CBD5E1 !important;
        color: #e1e6ed !important;
        
    }

    /* Primary CTA Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #38BDF8 0%, #22D3EE 100%) !important;
        color: #0B1020 !important;
        border: 0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 10px 20px !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #22D3EE 0%, #06B6D4 100%) !important;
        box-shadow: 0 12px 30px rgba(56, 189, 248, 0.35) !important;
        transform: translateY(-2px) !important;
    }s

    /* Tabs */
    [data-testid="stTabs"] {
        background: transparent !important;
    }

    /* Cards and containers */
    .stMetric, [data-testid="stMetricContainer"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(56, 189, 248, 0.1) !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }

    /* Data editor */
    [data-testid="stDataFrameContainer"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(56, 189, 248, 0.1) !important;
        border-radius: 8px !important;
    }

</style>
""", unsafe_allow_html = True )


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