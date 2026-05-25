import streamlit as st
from datetime import datetime
import api_client
import requests as http_requests

def activity_logs():

    # Initialize session state
    if "log_filter_action" not in st.session_state:
        st.session_state.log_filter_action = "All"
    if "log_filter_user" not in st.session_state:
        st.session_state.log_filter_user = "All Users"

    # ── Fetch logs from backend ──
    try:
        all_logs = api_client.get_activity_logs()
    except http_requests.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        all_logs = []
    except http_requests.HTTPError as e:
        st.error(f"Backend error: {e}")
        all_logs = []

    # Normalize: backend returns dicts
    unique_actions = sorted(set(log["action"] for log in all_logs))
    unique_users = sorted(set(
        f"User {log['user_id']}" if log["user_id"] else "System"
        for log in all_logs
    ))

    st.markdown("""
    <div class="admin-card">
        <div class="admin-title">📊 Activity Monitoring</div>
        <div class="admin-content">Monitor important system activities and security events.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filter Section ──
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

    # ── Apply filters ──
    filtered_logs = all_logs

    if action_filter != "All":
        filtered_logs = [log for log in filtered_logs if log["action"] == action_filter]

    if user_filter != "All Users":
        if user_filter == "System":
            filtered_logs = [log for log in filtered_logs if log["user_id"] is None]
        else:
            uid = int(user_filter.split()[-1])
            filtered_logs = [log for log in filtered_logs if log["user_id"] == uid]

    # Sort newest first
    filtered_logs = sorted(filtered_logs, key=lambda x: x["created_at"], reverse=True)

    # ── Display ──
    if filtered_logs:
        log_data = [
            {
                "ID": log["id"],
                "User": f"User {log['user_id']}" if log["user_id"] else "System",
                "Action": log["action"],
                "Details": log["details"] if log["details"] else "-",
                "Timestamp": str(log["created_at"])[:19]
            }
            for log in filtered_logs
        ]
        st.dataframe(log_data, use_container_width=True, hide_index=True)
        st.info(f"📋 Total records: {len(log_data)}")
    else:
        if all_logs:
            st.warning("❌ No logs found matching the filters.")
        else:
            st.info("📋 No activity logs available yet.")

    st.divider()

    # ── Export Section ──
    st.markdown("""
    <div class="admin-card">
        <div class="admin-title">📥 Export Logs</div>
        <div class="admin-content">Download system logs for backup or audit purposes.</div>
    </div>
    """, unsafe_allow_html=True)

    import json as json_lib
    import csv
    import io

    col1, col2, col3 = st.columns([1, 1, 2])

    # Build export data from filtered logs
    export_data = [
        {
            "id": log["id"],
            "user_id": log["user_id"],
            "action": log["action"],
            "details": log["details"],
            "created_at": str(log["created_at"])[:19]
        }
        for log in filtered_logs
    ]

    with col1:
        if export_data:
            # CSV export
            csv_buffer = io.StringIO()
            if export_data:
                writer = csv.DictWriter(csv_buffer, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
            st.download_button(
                label="📥 Export CSV",
                data=csv_buffer.getvalue(),
                file_name=f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📥 Export CSV", use_container_width=True, disabled=True)

    with col2:
        if export_data:
            st.download_button(
                label="📥 Export JSON",
                data=json_lib.dumps(export_data, indent=2, default=str),
                file_name=f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.button("📥 Export JSON", use_container_width=True, disabled=True)

    with col3:
        st.write("")