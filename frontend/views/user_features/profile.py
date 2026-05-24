import streamlit as st
from datetime import datetime
from dataclasses import dataclass

# Mock User Data Model
@dataclass
class UserProfile:
    id: int
    username: str
    email: str
    full_name: str
    organization: str
    country: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime

def get_mock_user_profile() -> UserProfile:
    """Get mock user profile"""
    return UserProfile(
        id=st.session_state.get("user_id", 1),
        username=st.session_state.get("username", "user"),
        email="user@example.com",
        full_name="John Doe",
        organization="Example Corporation",
        country="United States",
        role=st.session_state.get("role", "user"),
        is_active=True,
        created_at=datetime.now(),
        last_login=datetime.now()
    )

def profile():
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title("Profile & Settings")
    st.markdown("Manage your account information and preferences")
    
    st.divider()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Profile", " Security", " Preferences"])
    
    with tab1:
        st.subheader("User Profile")
        
        user = get_mock_user_profile()
        
        # Profile info
        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #48bb78; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #48bb78; margin-bottom: 10px;">✅ Account Information</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
        <div><strong>Username:</strong> {user.username}</div>
        <div><strong>Role:</strong> <span style="background-color: #4299e1; padding: 2px 8px; border-radius: 3px;">{user.role.upper()}</span></div>
        <div><strong>Email:</strong> {user.email}</div>
        <div><strong>Full Name:</strong> {user.full_name}</div>
        <div><strong>Organization:</strong> {user.organization}</div>
        <div><strong>Country:</strong> {user.country}</div>
        </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Edit profile form
        st.markdown("**✏️ Edit Profile**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_full_name = st.text_input(
                "Full Name:",
                value=user.full_name,
                key="edit_fullname"
            )
            
            new_organization = st.text_input(
                "Organization:",
                value=user.organization,
                key="edit_org"
            )
        
        with col2:
            new_email = st.text_input(
                "Email:",
                value=user.email,
                key="edit_email"
            )
            
            new_country = st.text_input(
                "Country:",
                value=user.country,
                key="edit_country"
            )
        
        st.divider()
        
        if st.button("💾 Save Changes", use_container_width=True, key="save_profile"):
            st.success("""
            ✅ Profile Updated Successfully!
            
            Your profile information has been updated.
            """)
        
        st.divider()
        
        # Account status
        st.markdown("**📊 Account Status**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Created:** {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        with col2:
            st.write(f"**Last Login:** {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
    
    with tab2:
        st.subheader("Security Settings")
        
        # Password change section
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
            password_strength = len(new_password)
            if password_strength < 8:
                strength_text = "🔴 Weak"
                strength_color = "#f56565"
            elif password_strength < 12:
                strength_text = "🟡 Medium"
                strength_color = "#ecc94b"
            else:
                strength_text = "🟢 Strong"
                strength_color = "#48bb78"
            
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
                st.success("✅ Password Changed Successfully!")
        
        st.divider()
        
        # Two-factor authentication
        st.markdown("**🔑 Two-Factor Authentication (2FA)**")
        
        enable_2fa = st.checkbox(
            "Enable Two-Factor Authentication",
            value=False,
            key="enable_2fa"
        )
        
        if enable_2fa:
            st.info("""
            Two-factor authentication adds an extra layer of security to your account.
            You'll need to enter a code from your authenticator app in addition to your password when logging in.
            """)
            
            if st.button("📱 Set Up 2FA", use_container_width=True, key="setup_2fa"):
                st.success("✅ 2FA Setup Complete!")
        
        st.divider()
        
        # Active Sessions
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
        
        # Notification preferences
        st.markdown("**🔔 Notifications**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox(" Email Notifications", value=True, key="pref_email_notif")
            st.checkbox(" Certificate Expiry Alerts", value=True, key="pref_cert_alerts")
        
        with col2:
            st.checkbox(" Request Approvals", value=True, key="pref_approve_notif")
            st.checkbox(" Request Rejections", value=True, key="pref_reject_notif")
        
        st.divider()
        
        # Display preferences
        st.markdown("**🎨 Display Settings**")
        
        theme = st.selectbox(
            "Theme:",
            ["Dark", "Light", "Auto"],
            key="pref_theme"
        )
        
        items_per_page = st.number_input(
            "Items per page:",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            key="pref_items_page"
        )
        
        st.divider()
        
        # Language
        st.markdown("**🌐 Language**")
        
        language = st.selectbox(
            "Preferred Language:",
            ["English", "Vietnamese", "Spanish", "French", "German"],
            key="pref_language"
        )
        
        st.divider()
        
        if st.button("💾 Save Preferences", use_container_width=True, key="save_preferences"):
            st.success("✅ Preferences Saved Successfully!")
