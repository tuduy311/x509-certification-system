import streamlit as st
from datetime import datetime
import api.api_client as api_client
import requests as http_requests


def profile():

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("👤 Settings")
    st.markdown("Manage your account information and preferences")
    st.divider()

    tab1, tab2 = st.tabs(["🔒 Security", "⚙️ Preferences"])

    with tab1:
        st.subheader("Security Settings")

        # ── Header card ──
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px; padding: 20px; margin-bottom: 15px;">
            <div style="font-size:18px; font-weight:bold; color:#ffffff;">🔒 Change Password</div>
            <div style="font-size:14px; color:#cbd5e1; line-height:2;">
                Update your account password securely.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        col1, _, col2 = st.columns([1, 0.4, 1])

        with col1:
            st.subheader("Password Update")

            current_password = st.text_input(
                "Current Password",
                type="password",
                help="Enter your current password",
                key="user_current_pwd"
            )

            new_password = st.text_input(
                "New Password",
                type="password",
                help="Min 8 chars, uppercase, lowercase, number, special character",
                key="user_new_pwd"
            )

            confirm_password = st.text_input(
                "Confirm New Password",
                type="password",
                help="Re-enter your new password",
                key="user_confirm_pwd"
            )

            # Password strength indicator
            if new_password:
                l = len(new_password)
                has_upper = any(c.isupper() for c in new_password)
                has_lower = any(c.islower() for c in new_password)
                has_digit = any(c.isdigit() for c in new_password)
                has_special = any(c in "!@#$%^&*" for c in new_password)
                score = sum([l >= 8, has_upper, has_lower, has_digit, has_special])
                if score <= 2:
                    strength_text, strength_color = "🔴 Weak", "#f56565"
                elif score == 3 or score == 4:
                    strength_text, strength_color = "🟡 Medium", "#ecc94b"
                else:
                    strength_text, strength_color = "🟢 Strong", "#48bb78"

                st.markdown(f"""
                <div style="background-color: {strength_color}20; border-left: 4px solid {strength_color};
                            border-radius: 5px; padding: 10px; margin-top: 8px;">
                <strong style="color: {strength_color};">Password Strength: {strength_text}</strong>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            if st.button("🔐 Change Password", type="primary", key="btn_user_change_pwd"):
                errors = []
                if not current_password:
                    errors.append("Current password is required")
                if not new_password:
                    errors.append("New password is required")
                if not confirm_password:
                    errors.append("Password confirmation is required")
                if new_password and confirm_password and new_password != confirm_password:
                    errors.append("Passwords do not match")
                if current_password and new_password and current_password == new_password:
                    errors.append("New password cannot be the same as current password")
                if new_password:
                    if len(new_password) < 8:
                        errors.append("Password must be at least 8 characters long")
                    if not any(c.isupper() for c in new_password):
                        errors.append("Password must contain uppercase letters")
                    if not any(c.islower() for c in new_password):
                        errors.append("Password must contain lowercase letters")
                    if not any(c.isdigit() for c in new_password):
                        errors.append("Password must contain numbers")
                    if not any(c in "!@#$%^&*" for c in new_password):
                        errors.append("Password must contain special characters (!@#$%^&*)")

                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    try:
                        api_client.change_password(current_password, new_password, confirm_password)
                        st.success(
                            f"Password changed successfully!\n\n"
                            f"**Details:**\n"
                            f"- Changed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"- User: {st.session_state.get('username', 'unknown')}\n\n"
                            f"⚠️ Please log out and log in again with your new password.",
                            icon="✅"
                        )
                    except http_requests.HTTPError as e:
                        if e.response is not None:
                            if e.response.status_code == 422:
                                try:
                                    validation_errors = e.response.json().get("detail", [])
                                    for err in validation_errors:
                                        field = err.get("loc", ["body"])[-1]
                                        msg = err.get("msg", "Invalid format.")
                                        st.error(f"⚠️ Validation Error ({field}): {msg}")
                                except Exception:
                                    st.error("❌ Input data format is not accepted by the server.")
                            else:
                                try:
                                    error_detail = e.response.json().get("detail", "Bad Request")
                                    st.error(f"❌ {error_detail}")
                                except Exception:
                                    st.error(f"❌ Error {e.response.status_code}: {e.response.text}")
                        else:
                            st.error(f"❌ Error: {str(e)}")
                    except http_requests.ConnectionError:
                        st.error("❌ Cannot connect to backend.")

        with col2:
            st.subheader("Security Requirements")
            st.markdown("""
        ✅ **Your new password must:**

        - Have at least **8 characters**
        - Contain **uppercase letters** (A-Z)
        - Contain **lowercase letters** (a-z)
        - Contain **numbers** (0-9)
        - Contain **special characters** (!@#$%^&*)

        ⚠️ **Tips:**
        - Don't use personal information
        - Don't reuse old passwords
        - Change password every 90 days
        - Keep it confidential
        """)

        st.divider()

        # Security info card
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px; padding: 20px; margin-top: 10px;">
            <div style="font-size:18px; font-weight:bold; color:#ffffff; margin-bottom:10px;">🛡️ Security Information</div>
            <div style="font-size:14px; color:#cbd5e1; line-height:2;">
            <ul>
                <li>Your password is never stored in plain text</li>
                <li>Change your password regularly for better security</li>
                <li>Avoid sharing your password with anyone</li>
                <li>Password changes are logged for audit purposes</li>
            </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)



    with tab2:
        st.subheader("Preferences")

        st.markdown("**🔔 Notifications**")

        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("📧 Email Notifications", value=True, key="pref_email_notif")
            st.checkbox("⏰ Certificate Expiry Alerts", value=True, key="pref_cert_alerts")
        with col2:
            st.checkbox("✅ Request Approvals", value=True, key="pref_approve_notif")
            st.checkbox("❌ Request Rejections", value=True, key="pref_reject_notif")

        st.divider()

        st.markdown("**🎨 Display Settings**")

        theme = st.selectbox(
            "Theme:",
            ["Dark", "Light", "Auto"],
            key="pref_theme"
        )

        items_per_page = st.number_input(
            "Items per page:",
            min_value=5, max_value=50, value=10, step=5,
            key="pref_items_page"
        )

        st.divider()

        st.markdown("**🌐 Language**")

        language = st.selectbox(
            "Preferred Language:",
            ["English", "Vietnamese", "Spanish", "French", "German"],
            key="pref_language"
        )

        st.divider()

        if st.button("💾 Save Preferences", use_container_width=True, key="save_preferences"):
            st.success("✅ Preferences Saved Successfully!")
