import streamlit as st
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
from enum import Enum

# Enums
class CertStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

# Mock Data Models
@dataclass
class CertificateRequestOut:
    id: int
    certificate_id: int
    user_id: int
    reason: str
    status: CertStatus
    created_at: datetime

# Mock Data Generator
def get_mock_requests() -> List[CertificateRequestOut]:
    """Generate mock certificate requests data"""
    return [
        CertificateRequestOut(
            id=1,
            certificate_id=101,
            user_id=5,
            reason="Initial certificate request for John Doe",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(days=2)
        ),
        CertificateRequestOut(
            id=2,
            certificate_id=102,
            user_id=6,
            reason="Certificate renewal request",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(days=1)
        ),
        CertificateRequestOut(
            id=3,
            certificate_id=103,
            user_id=7,
            reason="Emergency certificate request",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(hours=12)
        ),
        CertificateRequestOut(
            id=4,
            certificate_id=104,
            user_id=8,
            reason="Regular server certificate",
            status=CertStatus.APPROVED,
            created_at=datetime.now() - timedelta(days=5)
        ),
        CertificateRequestOut(
            id=5,
            certificate_id=105,
            user_id=9,
            reason="Client authentication certificate",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(days=3)
        ),
    ]

def approve_requests():
  
    # Initialize session state
    if "approval_data" not in st.session_state:
        st.session_state.approval_data = {}
    
    # Back to Dashboard Button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    # Header Section
    st.title(" Approve Certificate Requests")
    st.markdown("Manage and approve pending X.509 certificate requests")
    st.divider()


    # Get mock data
    all_requests = get_mock_requests()
    
    # Filter PENDING requests only
    pending_requests = [req for req in all_requests if req.status == CertStatus.PENDING]
    
   
    
    # Check if there are pending requests
    if not pending_requests:
        st.info("ℹ️ No pending certificate requests at the moment.")
        return
    
    # Request Selection Section
    st.subheader("Select Request")
    
    # Create display options for selectbox
    request_options = [
        f"Request #{req.id} - User {req.user_id} (Created: {req.created_at.strftime('%Y-%m-%d %H:%M')})"
        for req in pending_requests
    ]
    
    selected_option = st.selectbox(
        "Choose a certificate request to review:",
        range(len(pending_requests)),
        format_func=lambda i: request_options[i],
        key="request_select"
    )
    
    selected_request = pending_requests[selected_option]
    
    st.divider()
    
    # Request Details Section
    st.subheader("Request Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Request ID:** {selected_request.id}")
        st.write(f"**Certificate ID:** {selected_request.certificate_id}")
        st.write(f"**User ID:** {selected_request.user_id}")
    
    with col2:
        st.write(f"**Status:** {selected_request.status.value}")
        st.write(f"**Created:** {selected_request.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Days Ago:** {(datetime.now() - selected_request.created_at).days} day(s)")
    
    st.write(f"**Reason:** {selected_request.reason}")
    
    st.divider()
    
    # Approval Configuration Section
    st.subheader("Approval Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        validity_days = st.number_input(
            "Certificate Validity (days)",
            min_value=1,
            max_value=3650,
            value=365,
            step=1,
            help="How many days should this certificate be valid?"
        )
    
    with col2:
        hash_algorithm = st.selectbox(
            "Hash Algorithm",
            ["SHA-256", "SHA-384", "SHA-512"],
            help="Select the hash algorithm for the certificate"
        )
    
    # Approval button
    if st.button("Approve Certificate", type="primary"):
        # Store approval data in session state
        approval_key = f"request_{selected_request.id}"
        st.session_state.approval_data[approval_key] = {
            "request_id": selected_request.id,
            "validity_days": validity_days,
            "hash_algorithm": hash_algorithm,
            "approved_at": datetime.now()
        }
        
        # Display success message
        st.success(
            f"✅ Certificate Request #{selected_request.id} approved successfully!\n\n"
            f"**Details:**\n"
            f"- Certificate ID: {selected_request.certificate_id}\n"
            f"- User ID: {selected_request.user_id}\n"
            f"- Validity: {validity_days} days\n"
            f"- Hash Algorithm: {hash_algorithm}",
            icon="✅"
        )
        
    st.divider()
    
    # Summary Section
    st.subheader("Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Selection:**")
        st.write(f"- Request ID: {selected_request.id}")
        st.write(f"- Validity: {validity_days} days")
        st.write(f"- Algorithm: {hash_algorithm}")
    
    with col2:
        st.write("**Previously Approved:**")
        if st.session_state.approval_data:
            for key, data in st.session_state.approval_data.items():
                st.write(f"- Request #{data['request_id']} ✅")
        else:
            st.write("- None yet")


    st.divider()
     # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔄 Total Pending", len(pending_requests))
    with col2:
        st.metric("📋 Total Requests", len(all_requests))
    with col3:
        st.metric("✅ Approved", len([r for r in all_requests if r.status == CertStatus.APPROVED]))
    
    st.divider()
