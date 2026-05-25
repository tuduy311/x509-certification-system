import streamlit as st
from datetime import datetime
import api_client
import requests as http_requests

from styles.dashboard import Dashboard_CSS


def _validate_password(pwd: str):
    """Validate password strength. Returns (bool, message)."""
    if len(pwd) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in pwd):
        return False, "Password must contain uppercase letters"
    if not any(c.islower() for c in pwd):
        return False, "Password must contain lowercase letters"
    if not any(c.isdigit() for c in pwd):
        return False, "Password must contain numbers"
    if not any(c in "!@#$%^&*" for c in pwd):
        return False, "Password must contain special characters (!@#$%^&*)"
    return True, "Password is strong"


def change_password():
    st.markdown(Dashboard_CSS, unsafe_allow_html=True)

    # Initialize session state
    if "password_change_success" not in st.session_state:
        st.session_state.password_change_success = False

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    # Header
    st.markdown("""
    <div class="admin-card">
        <div class="admin-title">🔒 Change Admin Password</div>
        <div class="admin-content">Update administrator account password securely.</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Password change form
    col1, _, col2 = st.columns([1, 0.4, 1])

    with col1:
        st.subheader("Password Update")

        # Current password (client-side only – backend uses JWT identity)
        current_password = st.text_input(
            "Current Password",
            type="password",
            help="Enter your current admin password"
        )

        # New password
        new_password = st.text_input(
            "New Password",
            type="password",
            help="Enter your new password (min 8 chars, must include uppercase, lowercase, number, special char)"
        )

        # Confirm new password
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            help="Re-enter your new password"
        )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if st.button("🔐 Update Password", type="primary"):
            errors = []

            if not current_password:
                errors.append("Current password is required")
            if not new_password:
                errors.append("New password is required")
            if not confirm_password:
                errors.append("Password confirmation is required")
            if new_password and confirm_password and new_password != confirm_password:
                errors.append("Passwords do not match")
            if new_password:
                is_valid, msg = _validate_password(new_password)
                if not is_valid:
                    errors.append(msg)
            if current_password and new_password and current_password == new_password:
                errors.append("New password cannot be the same as current password")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    api_client.change_password(new_password)
                    st.success(
                        f"✅ Password changed successfully!\n\n"
                        f"**Details:**\n"
                        f"- Changed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"- Admin: {st.session_state.username}\n\n"
                        f"⚠️ Please log out and log in again with your new password.",
                        icon="✅"
                    )
                except http_requests.HTTPError as e:
                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                    st.error(f"❌ Backend error: {detail}")
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

    # Security info
    st.markdown("""
    <div class="admin-card">
        <div class="admin-title">🛡️ Security Information</div>
        <div class="admin-content">
        <ul>
            <li>Your password is never stored in plain text</li>
            <li>Change your password regularly for better security</li>
            <li>Avoid sharing your password with anyone</li>
            <li>Password changes are logged for audit purposes</li>
        </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
