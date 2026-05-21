import streamlit as st

from styles.auth_css import AUTH_CSS, LEFT_PANEL


 
def auth_page(users):

    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "login"

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