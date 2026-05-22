import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

# Enums
class CertStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

# Mock Data Model
@dataclass
class CertificateRequestOut:
    id: int
    user_id: int
    csr_pem: str
    status: CertStatus
    created_at: datetime

# Mock Data Generator
def get_mock_requests() -> List[CertificateRequestOut]:
    """Generate mock certificate requests data"""
    return [
        CertificateRequestOut(
            id=1,
            user_id=5,
            csr_pem="-----BEGIN CERTIFICATE REQUEST-----\nMIICljCCAX4CAQAwDQYJKoZIhvcNAQEBBQAwDTEL\nMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7\n-----END CERTIFICATE REQUEST-----",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(days=2)
        ),
        CertificateRequestOut(
            id=2,
            user_id=6,
            csr_pem="-----BEGIN CERTIFICATE REQUEST-----\nMIICljCCAX4CAQAwDQYJKoZIhvcNAQEBBQAwDTEL\nMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7\n-----END CERTIFICATE REQUEST-----",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(days=1)
        ),
        CertificateRequestOut(
            id=3,
            user_id=7,
            csr_pem="-----BEGIN CERTIFICATE REQUEST-----\nMIICljCCAX4CAQAwDQYJKoZIhvcNAQEBBQAwDTEL\nMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7\n-----END CERTIFICATE REQUEST-----",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(hours=12)
        ),
        CertificateRequestOut(
            id=4,
            user_id=8,
            csr_pem="-----BEGIN CERTIFICATE REQUEST-----\nMIICljCCAX4CAQAwDQYJKoZIhvcNAQEBBQAwDTEL\nMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7\n-----END CERTIFICATE REQUEST-----",
            status=CertStatus.REJECTED,
            created_at=datetime.now() - timedelta(days=5)
        ),
        CertificateRequestOut(
            id=5,
            user_id=9,
            csr_pem="-----BEGIN CERTIFICATE REQUEST-----\nMIICljCCAX4CAQAwDQYJKoZIhvcNAQEBBQAwDTEL\nMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7\n-----END CERTIFICATE REQUEST-----",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(days=3)
        ),
    ]

def reject_requests():
    
    # Initialize session state
    if "rejected_requests" not in st.session_state:
        st.session_state.rejected_requests = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title("Reject Certificate Requests")
    st.markdown("Review and reject pending certificate requests with detailed reasoning")
    
    st.divider()
    
    # Get mock data
    all_requests = get_mock_requests()
    
    # Filter PENDING requests only
    pending_requests = [req for req in all_requests if req.status == CertStatus.PENDING]
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔄 Pending", len(pending_requests))
    with col2:
        st.metric("❌ Rejected", len([r for r in all_requests if r.status == CertStatus.REJECTED]))
    with col3:
        st.metric("✅ Approved", len([r for r in all_requests if r.status == CertStatus.APPROVED]))
    with col4:
        st.metric("📊 Total", len(all_requests))
    
    st.divider()
    
    # Check if there are pending requests
    if not pending_requests:
        st.info("No pending certificate requests to review.")
        return
    
    # Request Selection Section
    st.subheader(" Select Request")
    
    # Create display options for selectbox
    request_options = [
        f"Request #{req.id} - User {req.user_id} (Created: {req.created_at.strftime('%Y-%m-%d %H:%M')})"
        for req in pending_requests
    ]
    
    selected_option = st.selectbox(
        "Choose a certificate request to review:",
        range(len(pending_requests)),
        format_func=lambda i: request_options[i],
        key="reject_request_select"
    )
    
    selected_request = pending_requests[selected_option]
    
    st.divider()
    
    # Request Details Section
    st.subheader(" Request Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Request ID:** {selected_request.id}")
        st.write(f"**User ID:** {selected_request.user_id}")
        st.write(f"**Status:** {selected_request.status.value}")
    
    with col2:
        st.write(f"**Created:** {selected_request.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Days Ago:** {(datetime.now() - selected_request.created_at).days} day(s)")
        st.write(f"**Hours Ago:** {int((datetime.now() - selected_request.created_at).total_seconds() / 3600)} hours")
    
    # CSR PEM Viewer
    with st.expander("📄 View Certificate Signing Request (CSR)"):
        st.markdown(f"""
        <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
        <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{selected_request.csr_pem}</pre>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Rejection Reason Section
    st.subheader(" Rejection Reason")
    
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
        f"⚠️ **Warning:** This action will reject request #{selected_request.id} and notify user {selected_request.user_id}. "
        f"The user will need to resubmit with corrections.",
        icon="⚠️"
    )
    
    # Rejection Action Section
    st.subheader(" Confirm Rejection")
    
    # Validation and confirmation
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
            if not confirm:
                st.error("❌ Please confirm the rejection")
            elif not details_provided:
                st.error("❌ Please confirm you have provided rejection details")
            elif not additional_details.strip():
                st.error("❌ Please provide detailed rejection reason")
            else:
                # Store rejection data
                rejection_record = {
                    "request_id": selected_request.id,
                    "user_id": selected_request.user_id,
                    "reason": rejection_reason,
                    "details": additional_details,
                    "rejected_at": datetime.now()
                }
                st.session_state.rejected_requests.append(rejection_record)
                
                # Display success message
                st.success(
                    f"✅ Request #{selected_request.id} rejected successfully!\n\n"
                    f"**Details:**\n"
                    f"- User ID: {selected_request.user_id}\n"
                    f"- Rejection Reason: {rejection_reason}\n"
                    f"- Rejected At: {rejection_record['rejected_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"- Notification sent to user",
                    icon="✅"
                )
                
                st.info(
                    "📌 User has been notified about the rejection and can resubmit with corrections.",
                    icon="ℹ️"
                )
    
    st.divider()
    
    # Summary Section
    st.subheader(" Rejection Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Selection:**")
        st.write(f"- Request ID: {selected_request.id}")
        st.write(f"- User ID: {selected_request.user_id}")
        st.write(f"- Reason: {rejection_reason}")
    
    with col2:
        st.write("**Previously Rejected:**")
        if st.session_state.rejected_requests:
            for idx, rejected in enumerate(st.session_state.rejected_requests, 1):
                st.write(f"- Request #{rejected['request_id']} ({rejected['reason']}) ❌")
        else:
            st.write("- None yet")
