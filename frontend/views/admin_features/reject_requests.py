import streamlit as st
from datetime import datetime
import api.api_client as api_client
import requests as http_requests
from api.helpers import BackendError


def reject_requests():

    # Initialize session state
    if "rejected_requests" not in st.session_state:
        st.session_state.rejected_requests = []
    # if "admin_requests_cache" not in st.session_state:
    #     st.session_state.admin_requests_cache = None
    # if "admin_certificates_cache" not in st.session_state:
    #     st.session_state.admin_certificates_cache = None

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("❌ Reject Certificate Requests")
    st.markdown("Review and reject pending certificate requests with detailed reasoning")
    st.divider()

    # ── Fetch requests and certificates from backend using cache ──
    # if st.session_state.admin_requests_cache is None or st.session_state.admin_certificates_cache is None:
    try:
        st.session_state.admin_requests_cache = api_client.get_all_requests()
        st.session_state.admin_certificates_cache = api_client.get_all_certificates()
    except (BackendError, http_requests.ConnectionError):
        return

    all_requests = st.session_state.admin_requests_cache
    pending_requests = [r for r in all_requests if r["status"] == "pending"]
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔄 Pending", len(pending_requests))
    with col2:
        st.metric("❌ Rejected", len([r for r in all_requests if r["status"] == "rejected"]))
    with col3:
        st.metric("✅ Approved", len([r for r in all_requests if r["status"] == "approved"]))
    with col4:
        st.metric("📊 Total", len(all_requests))

    st.divider()

    if not pending_requests:
        st.info("No pending certificate requests to review.")
        return

    # Request Selection
    st.subheader("Select Request")

    request_options = [
        f"Request #{r['id']} - User {r['user_id']} (Created: {r['created_at'][:16]})"
        for r in pending_requests
    ]

    selected_option = st.selectbox(
        "Choose a certificate request to review:",
        range(len(pending_requests)),
        format_func=lambda i: request_options[i],
        key="reject_request_select"
    )

    selected_request = pending_requests[selected_option]

    st.divider()

    # Request Details
    st.subheader("Request Details")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Request ID:** {selected_request['id']}")
        st.write(f"**User ID:** {selected_request['user_id']}")
        st.write(f"**Status:** {selected_request['status'].upper()}")

    with col2:
        st.write(f"**Created:** {selected_request['created_at'][:19]}")

    # CSR PEM Viewer
    with st.expander("📄 View Certificate Signing Request (CSR)"):
        st.code(selected_request["csr_pem"], language="text")

    st.divider()

    # Rejection Reason Section
    st.subheader("Rejection Reason")

    rejection_reason = st.selectbox(
        "Select rejection reason:",
        [
            "Invalid Documentation",
            "Incomplete Information",
            "Suspicious Activity",
            "Duplicate Request",
            "Invalid CSR Format",
            "Missing Required Fields",
            "Company Policy Violation",
            "Compliance Issues",
            "User Request",
            "Other"
        ],
        help="Select the primary reason for rejecting this request"
    )

    additional_details = st.text_area(
        "Additional Details (Required)",
        placeholder="Provide detailed explanation for the rejection...",
        height=120,
        help="Explain why this request is being rejected"
    )

    # Rejection Warning
    st.warning(
        f"**Warning:** This action will reject request #{selected_request['id']} "
        f"and notify user {selected_request['user_id']}. "
        f"The user will need to resubmit with corrections.",
        icon="⚠️"
    )

    # Confirm & Reject
    st.subheader("Confirm Rejection")

    col1, col2 = st.columns(2)

    with col1:
        confirm = st.checkbox(
            "I confirm I want to reject this certificate request",
            help="Check this box to enable the reject button"
        )

    with col2:
        details_provided = st.checkbox(
            "I have provided detailed rejection reason",
            help="Ensure you've explained the rejection clearly"
        )

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(
            "❌ Reject Request",
            use_container_width=True,
            type="primary",
            disabled=not (confirm and details_provided and additional_details.strip())
        ):
            try:
                api_client.reject_request(
                    request_id=selected_request["id"],
                    rejection_reason=rejection_reason,
                    rejection_details=additional_details
                )

                rejection_record = {
                    "request_id": selected_request["id"],
                    "user_id": selected_request["user_id"],
                    "reason": rejection_reason,
                    "details": additional_details,
                    "rejected_at": datetime.now()
                }
                st.session_state.rejected_requests.append(rejection_record)

                # Invalidate caches so we fetch fresh data from backend on the next run
                st.session_state.admin_requests_cache = None
                st.session_state.admin_certificates_cache = None

                st.success(
                    f"Request #{selected_request['id']} rejected successfully!\n\n"
                    f"**Details:**\n"
                    f"- User ID: {selected_request['user_id']}\n"
                    f"- Rejection Reason: {rejection_reason}\n"
                    f"- Rejected At: {rejection_record['rejected_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"- Notification sent to user",
                    icon="✅"
                )
                st.info(
                    "📌 User has been notified about the rejection and can resubmit with corrections.",
                    icon="ℹ️"
                )
            except (BackendError, http_requests.ConnectionError):
                pass

    st.divider()

    # Summary Section
    st.subheader("Rejection Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Current Selection:**")
        st.write(f"- Request ID: {selected_request['id']}")
        st.write(f"- User ID: {selected_request['user_id']}")
        st.write(f"- Reason: {rejection_reason}")

    with col2:
        st.write("**Previously Rejected (this session):**")
        if st.session_state.rejected_requests:
            for idx, rejected in enumerate(st.session_state.rejected_requests, 1):
                st.write(f"- Request #{rejected['request_id']} ({rejected['reason']}) ❌")
        else:
            st.write("- None yet")
