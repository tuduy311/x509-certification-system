import streamlit as st
import os

# Streamlit set configuration
st.set_page_config(
    page_title = "X.509 Certificate System",
    page_icon = "" ,
    layout = "wide",
    initial_sidebar_state = "expanded"
)


# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary: #667eea;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --background: #0f172a;
        --surface: #1e293b;
    }
    
   
    }
</style>
""", unsafe_allow_html=True)


# Main app
st.title("X.509 Certificate System")

if not st.session_state.authenticated:
    st.info("Please log in to access")
else:
    st.success(f"Logged in as: {st.session_state.username} ({st.session_state.role})")