import streamlit as st
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
from enum import Enum

# Enums
class RevocationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class RevocationReason(str, Enum):
    KEY_COMPROMISE = "Key Compromise"
    AFFILIATION_CHANGED = "Affiliation Changed"
    SUPERSEDED = "Superseded"
    CESSATION_OF_OPERATION = "Cessation of Operation"
    CERTIFICATE_HOLD = "Certificate Hold"
    REMOVE_FROM_CRL = "Remove from CRL"
    PRIVILEGE_WITHDRAWN = "Privilege Withdrawn"
    AA_COMPROMISE = "AA Compromise"

# Mock Data Models
@dataclass
class CertificateOut:
    id: int
    serial_number: str
    subject_dn: str
    status: str
    valid_from: datetime
    valid_to: datetime

@dataclass
class RevocationRequest:
    id: int
    certificate_id: int
    serial_number: str
    reason: str
    status: RevocationStatus
    created_at: datetime

# Mock Data Generators
def get_mock_user_certificates() -> List[CertificateOut]:
    """Get active user certificates"""
    return [
        CertificateOut(
            id=1,
            serial_number="01:A2:B3:C4:D5:E6:F7:08",
            subject_dn="CN=user@example.com,O=MyOrg,C=US",
            status="ACTIVE",
            valid_from=datetime.now() - timedelta(days=30),
            valid_to=datetime.now() + timedelta(days=335)
        ),
        CertificateOut(
            id=2,
            serial_number="02:B3:C4:D5:E6:F7:08:09",
            subject_dn="CN=user@example.com,O=MyOrg,C=US",
            status="ACTIVE",
            valid_from=datetime.now() - timedelta(days=100),
            valid_to=datetime.now() + timedelta(days=265)
        ),
    ]

def get_mock_revocation_requests() -> List[RevocationRequest]:
    """Get user's revocation requests"""
    return [
        RevocationRequest(
            id=1,
            certificate_id=1,
            serial_number="01:A2:B3:C4:D5:E6:F7:08",
            reason="Superseded",
            status=RevocationStatus.APPROVED,
            created_at=datetime.now() - timedelta(days=5)
        ),
        RevocationRequest(
            id=2,
            certificate_id=2,
            serial_number="02:B3:C4:D5:E6:F7:08:09",
            reason="Key Compromise",
            status=RevocationStatus.PENDING,
            created_at=datetime.now() - timedelta(days=2)
        ),
    ]

def revoke_certificate():
    
    # Initialize session state
    if "revoked_certs" not in st.session_state:
        st.session_state.revoked_certs = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Request Certificate Revocation")
    st.markdown("Request to revoke one of your certificates")
    
    st.divider()
    
    # Create tabs
    tab1, tab2 = st.tabs([" Request Revocation", " Revocation History"])
    
    with tab1:
        st.subheader("Create Revocation Request")
        
        # Get available certificates
        all_certificates = get_mock_user_certificates()
        
        if not all_certificates:
            st.warning("⚠️ No active certificates available to revoke.")
        else:
            # Certificate selection
            cert_options = [f"Cert #{c.id} - {c.serial_number}" for c in all_certificates]
            selected_idx = st.selectbox(
                "Select Certificate to Revoke:",
                range(len(all_certificates)),
                format_func=lambda i: cert_options[i],
                key="cert_to_revoke"
            )
            
            selected_cert = all_certificates[selected_idx]
            
            st.divider()
            
            # Certificate details
            st.markdown("**📄 Certificate Details:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**ID:** {selected_cert.id}")
                st.write(f"**Serial Number:** `{selected_cert.serial_number}`")
                st.write(f"**Subject:** `{selected_cert.subject_dn}`")
            
            with col2:
                st.write(f"**Valid From:** {selected_cert.valid_from.strftime('%Y-%m-%d')}")
                st.write(f"**Valid To:** {selected_cert.valid_to.strftime('%Y-%m-%d')}")
                days_left = (selected_cert.valid_to - datetime.now()).days
                st.write(f"**Expires In:** {days_left} days")
            
            st.divider()
            
            # Revocation reason
            st.markdown("**🔍 Revocation Reason:**")
            
            reason = st.selectbox(
                "Select reason for revocation:",
                options=[r.value for r in RevocationReason],
                key="revoke_reason"
            )
            
            additional_notes = st.text_area(
                "Additional Notes (optional):",
                placeholder="Provide any additional details about the revocation request...",
                height=100,
                key="revoke_notes"
            )
            
            st.divider()
            
            # Confirmation warning
            st.markdown(f"""
            <div style="background-color: #744210; border-left: 4px solid #ed8936; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="font-weight: bold; color: #ed8936; margin-bottom: 10px;">⚠️ Warning: This Action Is Permanent</div>
            <div style="color: #e0e0e0; font-size: 14px;">
            Once this certificate is revoked, it cannot be used for any operations. This action is irreversible.
            The certificate will be listed on the Certificate Revocation List (CRL).
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Revocation summary
            st.markdown(f"""
            <div style="background-color: #2d3748; border-left: 4px solid #f6ad55; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="font-weight: bold; color: #f6ad55; margin-bottom: 10px;">📋 Revocation Summary</div>
            <div style="color: #e0e0e0; font-size: 14px;">
            <div style="margin: 5px 0;"><strong>Certificate ID:</strong> {selected_cert.id}</div>
            <div style="margin: 5px 0;"><strong>Serial Number:</strong> {selected_cert.serial_number}</div>
            <div style="margin: 5px 0;"><strong>Reason:</strong> {reason}</div>
            <div style="margin: 5px 0;"><strong>Request Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            confirm = st.checkbox(
                "✓ I understand this action is permanent and cannot be undone",
                key="confirm_revoke"
            )
            
            if st.button(
                "🚫 Submit Revocation Request",
                disabled=not confirm,
                key="btn_submit_revoke",
                use_container_width=True
            ):
                new_revocation = {
                    "id": len(st.session_state.revoked_certs) + 1,
                    "cert_id": selected_cert.id,
                    "serial_number": selected_cert.serial_number,
                    "reason": reason,
                    "timestamp": datetime.now()
                }
                st.session_state.revoked_certs.append(new_revocation)
                
                st.success(f"""
                ✅ Revocation Request Submitted Successfully!
                
                **Request Details:**
                - **Request ID:** {new_revocation['id']}
                - **Certificate ID:** {selected_cert.id}
                - **Serial Number:** {selected_cert.serial_number}
                - **Revocation Reason:** {reason}
                - **Submitted:** {new_revocation['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                
                Your revocation request has been submitted for review.
                """)
    
    with tab2:
        st.subheader("Revocation Request History")
        
        revocation_requests = get_mock_revocation_requests()
        
        if not revocation_requests:
            st.info("No revocation requests yet.")
        else:
            # Display stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("⏳ Pending", len([r for r in revocation_requests if r.status == RevocationStatus.PENDING]))
            with col2:
                st.metric("✅ Approved", len([r for r in revocation_requests if r.status == RevocationStatus.APPROVED]))
            with col3:
                st.metric("❌ Rejected", len([r for r in revocation_requests if r.status == RevocationStatus.REJECTED]))
            with col4:
                st.metric("📊 Total", len(revocation_requests))
            
            st.divider()
            
            # Display requests as expandable sections
            for req in revocation_requests:
                status_icon = "🟢" if req.status == RevocationStatus.APPROVED else ("🟠" if req.status == RevocationStatus.PENDING else "🔴")
                
                with st.expander(f"{status_icon} Request #{req.id} - Serial {req.serial_number} ({req.status.value})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Request ID:** {req.id}")
                        st.write(f"**Certificate ID:** {req.certificate_id}")
                    
                    with col2:
                        st.write(f"**Reason:** {req.reason}")
                        st.write(f"**Status:** {req.status.value}")
                    
                    with col3:
                        st.write(f"**Requested:** {req.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Days Ago:** {(datetime.now() - req.created_at).days} day(s)")
