import streamlit as st
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
from enum import Enum

# Enums
class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# Mock Data Models
@dataclass
class CertificateRequestOut:
    id: int
    user_id: int
    csr_pem: str
    status: RequestStatus
    created_at: datetime
    reason: str

# Mock Data Generator
def get_mock_user_requests() -> List[CertificateRequestOut]:
    """Generate mock certificate requests for current user"""
    return [
        CertificateRequestOut(
            id=1,
            user_id=st.session_state.get("user_id", 1),
            csr_pem="-----BEGIN CERTIFICATE REQUEST-----\nMIICljCCAX4CAQAwDQYJKoZIhvcNAQEBBQAwDTEL\nMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7\n-----END CERTIFICATE REQUEST-----",
            status=RequestStatus.PENDING,
            created_at=datetime.now() - timedelta(days=2),
            reason="Initial certificate request for TLS/SSL"
        ),
        CertificateRequestOut(
            id=2,
            user_id=st.session_state.get("user_id", 1),
            csr_pem="-----BEGIN CERTIFICATE REQUEST-----\nMIICljCCAX4CAQAwDQYJKoZIhvcNAQEBBQAwDTEL\nMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7\n-----END CERTIFICATE REQUEST-----",
            status=RequestStatus.APPROVED,
            created_at=datetime.now() - timedelta(days=10),
            reason="Web server certificate renewal"
        ),
        CertificateRequestOut(
            id=3,
            user_id=st.session_state.get("user_id", 1),
            csr_pem="-----BEGIN CERTIFICATE REQUEST-----\nMIICljCCAX4CAQAwDQYJKoZIhvcNAQEBBQAwDTEL\nMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7\n-----END CERTIFICATE REQUEST-----",
            status=RequestStatus.REJECTED,
            created_at=datetime.now() - timedelta(days=20),
            reason="Client authentication certificate"
        ),
    ]

def request_certificate():
    
    # Initialize session state
    if "user_requests" not in st.session_state:
        st.session_state.user_requests = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Request Certificate")
    st.markdown("Submit a new certificate request with your Certificate Signing Request (CSR)")
    
    st.divider()
    
    # Create tabs
    tab1, tab2 = st.tabs([" New Request", " My Requests"])
    
    with tab1:
        st.subheader("Create Certificate Request")
        
        col1, col2 = st.columns(2)
        
        with col1:
            common_name = st.text_input(
                "Common Name (CN):",
                placeholder="example.com or your name",
                key="req_cn"
            )
            
            organization = st.text_input(
                "Organization (O):",
                placeholder="Your Organization",
                key="req_org"
            )
        
        with col2:
            country = st.text_input(
                "Country Code (C):",
                value="US",
                max_chars=2,
                key="req_country"
            )
            
            state = st.text_input(
                "State/Province (ST):",
                placeholder="California",
                key="req_state"
            )
        
        st.divider()
        
        # CSR Input
        st.markdown("**📄 Certificate Signing Request (CSR):**")
        
        csr_pem = st.text_area(
            "Paste your CSR in PEM format:",
            placeholder="-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
            height=150,
            key="csr_input"
        )
        
        st.divider()
        
        # Request Purpose
        request_purpose = st.selectbox(
            "Request Purpose:",
            options=[
                "Web Server (TLS/SSL)",
                "Client Authentication",
                "Email (S/MIME)",
                "Code Signing",
                "Other"
            ],
            key="req_purpose"
        )
        
        additional_info = st.text_area(
            "Additional Information (optional):",
            placeholder="Add any additional details about your request...",
            key="req_info"
        )
        
        st.divider()
        
        # Request Summary
        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #4299e1; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #4299e1; margin-bottom: 10px;">📋 Request Summary</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0;"><strong>Common Name:</strong> {common_name if common_name else 'Not specified'}</div>
        <div style="margin: 5px 0;"><strong>Organization:</strong> {organization if organization else 'Not specified'}</div>
        <div style="margin: 5px 0;"><strong>Purpose:</strong> {request_purpose}</div>
        <div style="margin: 5px 0;"><strong>CSR Status:</strong> {'✅ Provided' if csr_pem else '⏳ Pending'}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        confirm = st.checkbox(
            "✓ I confirm this certificate request",
            key="confirm_req"
        )
        
        if st.button(
            "📤 Submit Request",
            disabled=not (confirm and common_name and csr_pem),
            key="btn_submit_req",
            use_container_width=True
        ):
            new_request = {
                "id": len(st.session_state.user_requests) + 1,
                "cn": common_name,
                "org": organization,
                "purpose": request_purpose,
                "timestamp": datetime.now()
            }
            st.session_state.user_requests.append(new_request)
            
            st.success(f"""
            ✅ Certificate Request Submitted Successfully!
            
            **Request Details:**
            - **Request ID:** {new_request['id']}
            - **Common Name:** {common_name}
            - **Organization:** {organization}
            - **Purpose:** {request_purpose}
            - **Submitted:** {new_request['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
            
            Your request has been submitted for review. You will be notified when it is approved or rejected.
            """)
    
    with tab2:
        st.subheader("My Certificate Requests")
        
        user_requests = get_mock_user_requests()
        
        if not user_requests:
            st.info("No certificate requests yet.")
        else:
            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⏳ Pending", len([r for r in user_requests if r.status == RequestStatus.PENDING]))
            with col2:
                st.metric("✅ Approved", len([r for r in user_requests if r.status == RequestStatus.APPROVED]))
            with col3:
                st.metric("❌ Rejected", len([r for r in user_requests if r.status == RequestStatus.REJECTED]))
            
            st.divider()
            
            # Display requests as expandable sections
            for req in user_requests:
                status_color = "🟢" if req.status == RequestStatus.APPROVED else ("🟠" if req.status == RequestStatus.PENDING else "🔴")
                
                with st.expander(f"{status_color} Request #{req.id} - {req.reason} ({req.status.value})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Request ID:** {req.id}")
                        st.write(f"**Status:** {req.status.value}")
                        st.write(f"**Reason:** {req.reason}")
                    
                    with col2:
                        st.write(f"**Created:** {req.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Days Ago:** {(datetime.now() - req.created_at).days} day(s)")
                    
                    st.divider()
                    
                    # CSR Display
                    st.markdown("**📄 CSR (PEM):**")
                    st.markdown(f"""
                    <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
                    <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{req.csr_pem}</pre>
                    </div>
                    """, unsafe_allow_html=True)
