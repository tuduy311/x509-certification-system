import streamlit as st
from datetime import datetime
import api_client
import requests as http_requests


def profile():

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("👤 Profile & Settings")
    st.markdown("Manage your account information and preferences")
    st.divider()

    username = st.session_state.get("username", "unknown")
    role = st.session_state.get("role", "user")

    # Initialize editable profile fields in session state
    if "profile_full_name" not in st.session_state:
        st.session_state.profile_full_name = username
    if "profile_email" not in st.session_state:
        st.session_state.profile_email = f"{username}@example.com"
    if "profile_org" not in st.session_state:
        st.session_state.profile_org = "My Organization"
    if "profile_country" not in st.session_state:
        st.session_state.profile_country = "Vietnam"

    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔒 Security", "⚙️ Preferences"])

    with tab1:
        st.subheader("User Profile")

        # Profile display card
        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #48bb78; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #48bb78; margin-bottom: 10px;">✅ Account Information</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
        <div><strong>Username:</strong> {username}</div>
        <div><strong>Role:</strong> <span style="background-color: #4299e1; padding: 2px 8px; border-radius: 3px;">{role.upper()}</span></div>
        <div><strong>Email:</strong> {st.session_state.profile_email}</div>
        <div><strong>Full Name:</strong> {st.session_state.profile_full_name}</div>
        <div><strong>Organization:</strong> {st.session_state.profile_org}</div>
        <div><strong>Country:</strong> {st.session_state.profile_country}</div>
        </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("**✏️ Edit Profile**")
        st.info("ℹ️ Profile field changes are saved locally to this session. To update your password, use the Security tab.")

        col1, col2 = st.columns(2)
        with col1:
            new_full_name = st.text_input(
                "Full Name:",
                value=st.session_state.profile_full_name,
                key="edit_fullname"
            )
            new_org = st.text_input(
                "Organization:",
                value=st.session_state.profile_org,
                key="edit_org"
            )
        with col2:
            new_email = st.text_input(
                "Email:",
                value=st.session_state.profile_email,
                key="edit_email"
            )
            new_country = st.text_input(
                "Country:",
                value=st.session_state.profile_country,
                key="edit_country"
            )

        st.divider()

        if st.button("💾 Save Changes", use_container_width=True, key="save_profile"):
            st.session_state.profile_full_name = new_full_name
            st.session_state.profile_email = new_email
            st.session_state.profile_org = new_org
            st.session_state.profile_country = new_country
            st.success("✅ Profile Updated Successfully!")

        st.divider()

        st.markdown("**📊 Account Status**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Session Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        with col2:
            st.write(f"**Status:** 🟢 Active")

    with tab2:
        st.subheader("Security Settings")

        st.markdown("**🔐 Change Password**")

        col1, col2 = st.columns(2)
        with col1:
            current_password = st.text_input(
                "Current Password:",
                type="password",
                key="current_pwd"
            )
        with col2:
            new_password = st.text_input(
                "New Password:",
                type="password",
                key="new_pwd"
            )

        confirm_password = st.text_input(
            "Confirm New Password:",
            type="password",
            key="confirm_pwd"
        )

        # Password strength indicator
        if new_password:
            l = len(new_password)
            if l < 8:
                strength_text, strength_color = "🔴 Weak", "#f56565"
            elif l < 12:
                strength_text, strength_color = "🟡 Medium", "#ecc94b"
            else:
                strength_text, strength_color = "🟢 Strong", "#48bb78"

            st.markdown(f"""
            <div style="background-color: {strength_color}20; border-left: 4px solid {strength_color}; border-radius: 5px; padding: 10px;">
            <strong style="color: {strength_color};">Password Strength: {strength_text}</strong>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        if st.button("🔄 Change Password", use_container_width=True, key="btn_change_pwd"):
            if not current_password:
                st.error("❌ Please enter your current password")
            elif not new_password:
                st.error("❌ Please enter a new password")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")
            elif len(new_password) < 8:
                st.error("❌ Password must be at least 8 characters")
            else:
                try:
                    api_client.change_password(new_password)
                    st.success("✅ Password Changed Successfully! Please log in again with your new password.")
                except http_requests.HTTPError as e:
                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                    st.error(f"❌ Error: {detail}")
                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend.")

        st.divider()

        st.markdown("**💻 Active Sessions**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📱 Mobile", 0)
        with col2:
            st.metric("💻 Desktop", 1)
        with col3:
            st.metric("🌐 Other", 0)

    with tab3:
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
