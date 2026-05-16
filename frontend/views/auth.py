import streamlit as st

AUTH_CSS = """
<style>
/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Auth Panel Wrappers ── */
.auth-left-panel {
    background: #0f1a33;
    border: 2px solid rgba(255, 255, 255, 0.5);
    #border: 2px solid rgba(102, 126, 234, 0.5);

    border-radius: 14px;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);    
    padding: 40px 32px;
    min-height: 560px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.auth-left-panel > div:first-child,
.auth-left-panel > div:last-child {
    position: relative;
    z-index: 1;
}

.auth-panel-logo {
    width: 48px;
    height: 48px;
    background: rgba(255,255,255,0.15);
    border: 0.5px solid rgba(255,255,255,0.25);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 24px;
}

.auth-panel-title {
    font-size: 22px;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}

.auth-panel-subtitle {
    font-size: 15px;
    color: rgba(199,210,254,0.85);
    line-height: 1.6;
}

.auth-panel-status {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 16px;
}

.auth-panel-status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22c55e;
    flex-shrink: 0;
}

.auth-panel-status-text {
    font-size: 12px;
    color: rgba(199,210,254,0.7);
    font-weight: 500;
}

.auth-panel-features {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.auth-panel-feature {
    background: rgba(255,255,255,0.08);
    border: 0.5px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.auth-panel-feature-icon {
    font-size: 13px;
}

.auth-panel-feature-text {
    font-size: 12px;
    color: rgba(199,210,254,0.85);
}


/* ── Inputs ── */
.stTextInput input {
    background: #ffffff !important;
    border: 0.5px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    color: #374151 !important;
    padding: 10px 12px !important;
}
.stTextInput input::placeholder { color: #9ca3af !important; }
.stTextInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
.stTextInput label {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
}
 
/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 0.5px solid #e5e7eb !important;
    border-radius: 8px !important;
    color: #374151 !important;
    font-size: 14px !important;
}
[data-testid="stSelectbox"] label {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
}

div[data-testid="column"]:nth-of-type(3) {
    background: #0f1a33 !important;
    border: 2px solid rgba(255, 255, 255, 0.5);
    border-radius: 16px !important;
    padding: 50px !important;s
}

div[data-testid="column"]:nth-of-type(3) 
div[data-testid="column"]:nth-of-type(1) .stButton > button,
div[data-testid="column"]:nth-of-type(3) 
div[data-testid="column"]:nth-of-type(2) .stButton > button {
    background: #405b96 !important;
}




</style>
"""


LEFT_PANEL = """
<div class="auth-left-panel">
    <div>
        <div class="auth-panel-logo">🔐</div>
        <div class="auth-panel-title">X.509 Certificate System</div>
        <div class="auth-panel-subtitle">Hệ thống cấp phát<br>chứng chỉ số an toàn</div>
    </div>
    <div>
        <div class="auth-panel-status">
            <div class="auth-panel-status-dot"></div>
            <span class="auth-panel-status-text">Hệ thống hoạt động bình thường</span>
        </div>
        <div class="auth-panel-features">
            <div class="auth-panel-feature">
                <span class="auth-panel-feature-icon">🔒</span>
                <span class="auth-panel-feature-text">Mã hóa RSA 2048-bit</span>
            </div>
            <div class="auth-panel-feature">
                <span class="auth-panel-feature-icon">📋</span>
                <span class="auth-panel-feature-text">Chuẩn X.509 v3</span>
            </div>
            <div class="auth-panel-feature">
                <span class="auth-panel-feature-icon">⚡</span>
                <span class="auth-panel-feature-text">Cấp phát tức thời</span>
            </div>
        </div>
    </div>
</div>
"""
 

def auth_page(users):

    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "login"

    # Apply CSSs
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    with st.container():

        _, left_col, right_col, _ = st.columns([1, 1.5, 1.6, 1])

        with left_col:
            st.markdown(LEFT_PANEL, unsafe_allow_html=True)

        with right_col:
            # Heading
            tab = st.session_state.auth_tab

            heading = ("Chào mừng trở lại" if tab == "login" else "Tạo tài khoản")
            subheading = ("Đăng nhập để tiếp tục" if tab == "login" else "Điền thông tin để đăng kí")

            st.markdown(f"""
            <div style="margin-bottom:50px;">
                <div style="font-size:24px;font-weight:700;color:#1e1b4b;margin-bottom:3px;">
                    {heading}
                </div>
                <div style="font-size:16px;color:#9ca3af;">
                    {subheading}
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", use_container_width = True):
                    st.session_state.auth_tab = "login"
                    st.rerun()

            with col2:
                if st.button("Register", use_container_width = True):
                    st.session_state.auth_tab = "register"
                    st.rerun()

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            # ================= LOGIN =================
            if st.session_state.auth_tab == "login":

                username = st.text_input(
                    "Username",
                    placeholder="Ten_dang_nhap"
                )

                password = st.text_input(
                    "Password",
                    placeholder="••••••••",
                    type="password",
                )

                st.markdown(
                    "<div style='height:12px'></div>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "Đăng nhập →",
                    use_container_width=True
                ):

                    if not username or not password:
                        st.error("Vui lòng điền đầy đủ thông tin.")

                    elif username not in users:
                        st.error("Tên đăng nhập không tồn tại.")

                    elif users[username]["password"] != password:
                        st.error("Sai mật khẩu.")

                    else:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = users[username]["role"]
                        st.success("Đăng nhập thành công!")
                        st.rerun()

                st.markdown("""
                    <div style="text-align:center;margin-top:16px;font-size:13px;color:#9ca3af;">
                        Chưa có tài khoản?
                        <span style="color:#4f46e5;font-size:15px;font-weight:500;cursor:pointer;">
                            Đăng ký
                        </span> 
                    </div>
                    """, unsafe_allow_html=True)
                
            # ================= REGISTER =================
            else:
                new_username = st.text_input(
                    "Username",
                    placeholder="Ten_dang_nhap",
                )

                new_password = st.text_input(
                    "Password",
                    placeholder="••••••••",
                    type="password",
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    placeholder="••••••••",
                    type="password",
                )

                role = st.selectbox(
                    "Role",
                    ["user"]
                )

                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

                if st.button("Tạo tài khoản →", use_container_width=True
                ):

                    if not new_username or not new_password:
                        st.error("Vui lòng điền đầy đủ thông tin.")

                    elif new_username in users:
                        st.error("Tên đăng nhập đã tồn tại!")

                    elif new_password != confirm_password:
                        st.error("Mật khẩu xác nhân không đúng!")

                    else:
                        users[new_username] = {"password": new_password, "role": role}
                        st.success("Đăng ký thành công!")
                        st.session_state.auth_tab = "login"
                        st.rerun()