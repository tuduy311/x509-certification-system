import streamlit as st
import os

from views.auth import auth_page
from views.admin_dashboard import admin_dashboard
from views.user_dashboard import user_dashboard
from views.admin_features.approve_requests import approve_requests
from views.admin_features.reject_requests import reject_requests
from views.admin_features.change_password import change_password
from views.admin_features.revoke_certificate import revoke_certificate
from views.admin_features.certificate_standards import certificate_standards
from views.admin_features.generate_root_key_pair import generate_root_key_pair
from views.admin_features.generate_root_certificate import generate_root_certificate
from views.admin_features.update_crl import update_crl
from views.admin_features.issued_certificates import issued_certificates
from views.admin_features.revocation_requests import revocation_requests
from views.admin_features.renew_certificates import renew_certificates

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
    st.session_state.role = "admin"
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'current_feature' not in st.session_state:
    st.session_state.current_feature = None


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

        if st.button("logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()

# ___________ Routing _____________________
if not st.session_state.authenticated:
    auth_page(Test_User)

else:
    sidebar()
    
    # Feature-based routing for admin
    if st.session_state.role == "admin":
        if st.session_state.current_feature == "approve_requests":
            approve_requests()
        elif st.session_state.current_feature == "reject_requests":
            reject_requests()
        elif st.session_state.current_feature == "change_password":
            change_password()
        elif st.session_state.current_feature == "revoke_certificate":
            revoke_certificate()
        elif st.session_state.current_feature == "certificate_standards":
            certificate_standards()
        elif st.session_state.current_feature == "generate_root_key_pair":
            generate_root_key_pair()
        elif st.session_state.current_feature == "generate_root_certificate":
            generate_root_certificate()
        elif st.session_state.current_feature == "update_crl":
            update_crl()
        elif st.session_state.current_feature == "issued_certificates":
            issued_certificates()
        elif st.session_state.current_feature == "revocation_requests":
            revocation_requests()
        elif st.session_state.current_feature == "renew_certificates":
            renew_certificates()
        else:
            admin_dashboard()
    
    # User routing
    elif st.session_state.role == "user":
        user_dashboard()
