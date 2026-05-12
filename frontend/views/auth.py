import streamlit as st

Auth_CSS = """
<style>
    /* Input */
    .stTextInput input {
        background: #f7f6f2 !important;
        border: 0.5px solid rgba(0,0,0,0.2) !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        color: #1a1a1a !important; }

    .stTextInput input:focus {
        border-color: rgba(0,0,0,0.4) !important;
        box-shadow: 0 0 0 3px rgba(0,0,0,0.06) !important; }

        
    /* Button */
    .stButton > button {
        border: 0.5px solid rgba(0,0,0,0.15) !important;
        boder-radius: 8px !important;
        background: #f0ede8 !important;
        color: #555 !important;
        transition: all 0.15s !important;}

    .stButton > button:hover {
        background: #e8e4de !important;
        color: #555 !important; }

    [data-testid = "stButton-login_btn_active"] > button,
    [data-testid = "stButton-reg_btn_active"] >button {
        background: #1a1a1a !important;
        color: #fff !important;
        border-color: #1a1a1a !important; }    

    [data-testid = "stButton-submit_btn"] > button {
        }

     [data-testid = "stButton-submit_btn"] > button:hover {
        }

</style>
"""

def auth_page(users):

    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "login"

    # Them CSS
    st.markdown(Auth_CSS, unsafe_allow_html = True)

    with st.container():
        # Tao 3 cot de canh giua form login/register
        _, col_b, _ = st.columns([1,2,1])
        with col_b:
            # ___________ Menu ____________
            col1, col2 = st.columns(2)

            with col1:
                key1 = "login_btn_active" if st.session_state.auth_tab == "login" else "login_btn"
                if st.button("Login", use_container_width = True, key = key1):
                    st.session_state.auth_tab = "login"
                    st.rerun()
 
            with col2:
                key2 = "reg_btn_active" if st.session_state.auth_tab == "register" else "reg_btn"
                if st.button("Register", use_container_width = True):
                    st.session_state.auth_tab = "register"
                    st.rerun()

            st.markdown("<div style = 'height:8px'></div>", unsafe_allow_html = True) # tao khoang cach 

            # ____________ Login tab ___________
            if st.session_state.auth_tab == "login": 

                username = st.text_input("Username", placeholder = "Enter your username")
                password = st.text_input("Password", placeholder = "••••••••", type="password")

                st.markdown("<div style = 'height:8px'></div>", unsafe_allow_html = True) # tao khoang cach 

                if st.button("login", key = "submit_btn", use_container_width = True):
                    if not username or not password:
                        st.error("Vui long dien day du thong tin")
                    elif username not in users:
                        st.error("Ten dang nhap khong ton tai") 
                    elif users[username]["password"] != password:
                        st.error("Sai mat khau !")
                    else:
                        user_data = users[username]
                        if password == user_data["password"]:
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.role = user_data["role"]

                            st.success("Dang nhap thanh cong")
                            st.rerun()


            # ____________ Register tab ___________
            else:

                new_username = st.text_input("New Username", placeholder = "Enter your new username", key = "reg_username")
                new_password = st.text_input("New Password", placeholder = "••••••••", type = "password", key = "reg_password")

                role = st.selectbox("Role", ["user"]) # khong cho tao tk admin

                st.markdown("<div style = 'height:8px'></div>", unsafe_allow_html = True) # tao khoang cach 
                
                if st.button("create account", key = "submit_btn", use_container_width = True):
                    if not username or not password:
                        st.error("VUi long dien day du thong tin")
                    elif new_username in users:
                        st.error("Ten dang nhap da ton tai!")
                    else:
                        users[new_username] = {
                            "password" : new_password,
                            "role" : role
                        }

                        st.success("Dang ki thanh cong")
                        st.session_state.auth_tab = "login"
                        st.rerun()
