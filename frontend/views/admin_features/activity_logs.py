import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass

# Mock Data Model
@dataclass
class ActivityLogOut:
    id: int
    user_id: Optional[int]
    action: str
    details: Optional[str]
    created_at: datetime

# Mock Data Generator
def get_mock_activity_logs() -> List[ActivityLogOut]:
    """Generate mock activity logs data"""
    return [
        ActivityLogOut(
            id=1,
            user_id=1,
            action="Generated Root Certificate",
            details="Root CA certificate generated with RSA-2048",
            created_at=datetime.now() - timedelta(days=4, hours=14)
        ),
        ActivityLogOut(
            id=2,
            user_id=1,
            action="Approved Certificate Request",
            details="Request #102 approved for user_id=6, Validity: 365 days",
            created_at=datetime.now() - timedelta(days=4, hours=13, minutes=30)
        ),
        ActivityLogOut(
            id=3,
            user_id=1,
            action="Revoked Certificate",
            details="Certificate #105 revoked - Security concern",
            created_at=datetime.now() - timedelta(days=4, hours=13)
        ),
        ActivityLogOut(
            id=4,
            user_id=None,
            action="System Configuration Updated",
            details="Default certificate validity changed from 2 years to 1 year",
            created_at=datetime.now() - timedelta(days=3, hours=8)
        ),
        ActivityLogOut(
            id=5,
            user_id=2,
            action="Approved Certificate Request",
            details="Request #103 approved for user_id=7, Validity: 730 days",
            created_at=datetime.now() - timedelta(days=2, hours=10)
        ),
        ActivityLogOut(
            id=6,
            user_id=1,
            action="CRL Updated",
            details="Certificate Revocation List published",
            created_at=datetime.now() - timedelta(days=1, hours=16)
        ),
        ActivityLogOut(
            id=7,
            user_id=1,
            action="Rejected Certificate Request",
            details="Request #104 rejected - Invalid documentation",
            created_at=datetime.now() - timedelta(hours=5)
        ),
        ActivityLogOut(
            id=8,
            user_id=2,
            action="Password Changed",
            details="Admin password updated",
            created_at=datetime.now() - timedelta(hours=2)
        ),
    ]

def activity_logs():    
    # Initialize session state
    if "log_filter_action" not in st.session_state:
        st.session_state.log_filter_action = "All"
    if "log_filter_user" not in st.session_state:
        st.session_state.log_filter_user = "All Users"
    
    # Get mock data
    all_logs = get_mock_activity_logs()
    
    # Extract unique actions and users
    unique_actions = sorted(set([log.action for log in all_logs]))
    unique_users = sorted(set([f"Admin {log.user_id}" if log.user_id else "System" for log in all_logs]))
    
    st.markdown("""
    <div class="admin-card">
        <div class="admin-title">📊 Activity Monitoring</div>
        <div class="admin-content">Monitor important system activities and security events.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter Section
    col1, col2 = st.columns(2)
    with col1:
        action_filter = st.selectbox(
            "Filter by Action",
            ["All"] + unique_actions,
            key="log_filter_action"
        )
    with col2:
        user_filter = st.selectbox(
            "Filter by User",
            ["All Users"] + unique_users,
            key="log_filter_user"
        )
    
    # Apply filters
    filtered_logs = all_logs
    
    if action_filter != "All":
        filtered_logs = [log for log in filtered_logs if log.action == action_filter]
    
    if user_filter != "All Users":
        if user_filter == "System":
            filtered_logs = [log for log in filtered_logs if log.user_id is None]
        else:
            user_id = int(user_filter.split()[-1])
            filtered_logs = [log for log in filtered_logs if log.user_id == user_id]
    
    # Sort by created_at descending
    filtered_logs = sorted(filtered_logs, key=lambda x: x.created_at, reverse=True)
    
    # Display logs as dataframe
    if filtered_logs:
        log_data = [
            {
                "ID": log.id,
                "User": f"Admin {log.user_id}" if log.user_id else "System",
                "Action": log.action,
                "Details": log.details if log.details else "-",
                "Timestamp": log.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for log in filtered_logs
        ]
        st.dataframe(log_data, use_container_width=True, hide_index=True)
        st.info(f"📋 Total records: {len(log_data)}")
    else:
        st.warning("❌ No logs found matching the filters.")
    
    st.divider()
    
    # Export Section
    st.markdown("""
    <div class="admin-card">
        <div class="admin-title">📥 Export Logs</div>
        <div class="admin-content">Download system logs for backup or audit purposes.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.button("📥 Export CSV", use_container_width=True)
    with col2:
        st.button("📥 Export JSON", use_container_width=True)
    with col3:
        st.write("")  