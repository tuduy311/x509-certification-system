import streamlit as st
from datetime import datetime
import pandas as pd
import api_client
import requests as http_requests


def revocation_requests():

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("🔄 Certificate Revocation Requests")
    st.markdown("Review and process pending certificate revocation requests from users")
    st.divider()

    # ── Fetch from backend ──
    try:
        all_requests = api_client.get_revocation_requests()
    except http_requests.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return
    except http_requests.HTTPError as e:
        st.error(f"Backend error: {e}")
        return

    pending_requests = [r for r in all_requests if r["status"] == "pending"]

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏳ Pending", len(pending_requests))
    with col2:
        st.metric("✅ Approved", len([r for r in all_requests if r["status"] == "approved"]))
    with col3:
        st.metric("❌ Rejected", len([r for r in all_requests if r["status"] == "rejected"]))
    with col4:
        st.metric("📊 Total", len(all_requests))

    st.divider()

    # Tabs
    tab1, tab2 = st.tabs(["⏳ Pending Requests", "📋 All Requests"])

    # ── TAB 1: Pending Requests ──
    with tab1:
        st.subheader("Pending Revocation Requests")

        if not pending_requests:
            st.info("✅ No pending revocation requests.")
        else:
            # Summary table
            pending_data = [
                {
                    "Request ID": r["id"],
                    "Certificate ID": r["certificate_id"],
                    "User ID": r["user_id"],
                    "Reason": r["reason"],
                    "Requested": str(r["created_at"])[:16]
                }
                for r in pending_requests
            ]
            st.dataframe(pd.DataFrame(pending_data), use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Review Request")

            request_options = [
                f"Request #{r['id']} - Cert #{r['certificate_id']} - {r['reason']}"
                for r in pending_requests
            ]

            selected_idx = st.selectbox(
                "Select a revocation request to review:",
                range(len(pending_requests)),
                format_func=lambda i: request_options[i],
                key="pending_revocation_select"
            )

            selected_request = pending_requests[selected_idx]

            st.divider()
            st.subheader("Request Details")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Request ID:** {selected_request['id']}")
                st.write(f"**Certificate ID:** {selected_request['certificate_id']}")
                st.write(f"**User ID:** {selected_request['user_id']}")
                st.write(f"**Status:** {selected_request['status'].upper()}")

            with col2:
                created_at = str(selected_request["created_at"])[:19]
                st.write(f"**Requested:** {created_at}")
                days_pending = (datetime.now() - datetime.fromisoformat(created_at.replace("T", " "))).days if "T" in selected_request["created_at"] else 0
                st.write(f"**Days Pending:** {days_pending} day(s)")

            st.divider()

            st.markdown("**Revocation Reason:**")
            st.markdown(f"""
            <div style="background-color: #2d3748; border-left: 4px solid #ed8936; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="color: #e0e0e0; font-size: 15px;">{selected_request['reason']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # Verification checkboxes
            st.markdown("**✓ Verification Checklist:**")
            col1, col2 = st.columns(2)
            with col1:
                verify_identity = st.checkbox("User identity verified", key=f"verify_identity_{selected_request['id']}")
            with col2:
                verify_reason = st.checkbox("Revocation reason is valid", key=f"verify_reason_{selected_request['id']}")

            admin_notes = st.text_area(
                "Additional Notes (optional):",
                placeholder="Add any relevant notes about this revocation request...",
                key=f"admin_notes_{selected_request['id']}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "✅ Approve Revocation",
                    disabled=not (verify_identity and verify_reason),
                    key=f"approve_revoke_{selected_request['id']}",
                    use_container_width=True
                ):
                    try:
                        api_client.approve_revocation_request(selected_request["id"])
                        st.success(f"""
                        ✅ Revocation Request #{selected_request['id']} Approved!

                        **Details:**
                        - Certificate ID: {selected_request['certificate_id']}
                        - Revocation Reason: {selected_request['reason']}
                        - Approved At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                        Certificate has been revoked. Regenerate the CRL to publish the update.
                        """)
                        st.rerun()
                    except http_requests.HTTPError as e:
                        detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                        st.error(f"Error: {detail}")

            with col2:
                if st.button(
                    "❌ Reject Request",
                    key=f"reject_revoke_{selected_request['id']}",
                    use_container_width=True
                ):
                    try:
                        api_client.reject_revocation_request(selected_request["id"])
                        st.info(f"""
                        ❌ Revocation Request #{selected_request['id']} Rejected.

                        - Certificate ID: {selected_request['certificate_id']}
                        - Rejected At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                        Certificate remains active.
                        """)
                        st.rerun()
                    except http_requests.HTTPError as e:
                        detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                        st.error(f"Error: {detail}")

    # ── TAB 2: All Requests ──
    with tab2:
        st.subheader("All Revocation Requests")

        all_data = [
            {
                "ID": r["id"],
                "Certificate ID": r["certificate_id"],
                "User ID": r["user_id"],
                "Reason": r["reason"],
                "Status": r["status"].upper(),
                "Requested": str(r["created_at"])[:16]
            }
            for r in all_requests
        ]

        df_all = pd.DataFrame(all_data) if all_data else pd.DataFrame()

        status_filter = st.multiselect(
            "Filter by Status:",
            options=["PENDING", "APPROVED", "REJECTED"],
            default=["PENDING", "APPROVED", "REJECTED"],
            key="all_revocation_status_filter"
        )

        if status_filter and not df_all.empty:
            df_all = df_all[df_all["Status"].isin(status_filter)]

        st.dataframe(df_all, use_container_width=True, hide_index=True)
        st.info(f"📊 Showing {len(df_all)} of {len(all_requests)} requests")
