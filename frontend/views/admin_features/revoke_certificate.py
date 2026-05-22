import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

# Enums
class CertStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"

# Mock Data Model
@dataclass
class CertificateOut:
    id: int
    request_id: Optional[int]
    user_id: int
    serial_number: str
    cert_pem: str
    status: CertStatus
    valid_from: datetime
    valid_to: datetime
    created_at: datetime

# Mock Data Generator
def get_mock_certificates() -> List[CertificateOut]:
    """Generate mock certificate data"""
    return [
        CertificateOut(
            id=1,
            request_id=1,
            user_id=5,
            serial_number="001A2B3C4D5E6F7G8H9I",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ...\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=30),
            valid_to=datetime.now() + timedelta(days=335),
            created_at=datetime.now() - timedelta(days=30)
        ),
        CertificateOut(
            id=2,
            request_id=2,
            user_id=6,
            serial_number="002B3C4D5E6F7G8H9I0J",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ...\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=100),
            valid_to=datetime.now() + timedelta(days=265),
            created_at=datetime.now() - timedelta(days=100)
        ),
        CertificateOut(
            id=3,
            request_id=3,
            user_id=7,
            serial_number="003C4D5E6F7G8H9I0J1K",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ...\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=15),
            valid_to=datetime.now() + timedelta(days=350),
            created_at=datetime.now() - timedelta(days=15)
        ),
        CertificateOut(
            id=4,
            request_id=4,
            user_id=8,
            serial_number="004D5E6F7G8H9I0J1K2L",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ...\n-----END CERTIFICATE-----",
            status=CertStatus.REVOKED,
            valid_from=datetime.now() - timedelta(days=200),
            valid_to=datetime.now() + timedelta(days=165),
            created_at=datetime.now() - timedelta(days=200)
        ),
        CertificateOut(
            id=5,
            request_id=5,
            user_id=9,
            serial_number="005E6F7G8H9I0J1K2L3M",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ...\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=60),
            valid_to=datetime.now() + timedelta(days=305),
            created_at=datetime.now() - timedelta(days=60)
        ),
        CertificateOut(
            id=6,
            request_id=None,
            user_id=10,
            serial_number="006F7G8H9I0J1K2L3M4N",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ...\n-----END CERTIFICATE-----",
            status=CertStatus.EXPIRED,
            valid_from=datetime.now() - timedelta(days=400),
            valid_to=datetime.now() - timedelta(days=35),
            created_at=datetime.now() - timedelta(days=400)
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
    st.title(" Revoke Certificate")
    st.markdown("Revoke active certificates immediately")
    
    st.divider()
    
    # Get mock data
    all_certificates = get_mock_certificates()
    active_certificates = [cert for cert in all_certificates if cert.status == CertStatus.ACTIVE]
    
    # Check if there are active certificates
    if not active_certificates:
        st.info("ℹ️ No active certificates available to revoke.")
        return
    
    # Certificate Selection Section
    st.subheader(" Select Certificate")
    
    # Create display options for selectbox
    cert_options = [
        f"Cert #{cert.id} - User {cert.user_id} - {cert.serial_number} (Valid: {cert.valid_to.strftime('%Y-%m-%d')})"
        for cert in active_certificates
    ]
    
    selected_option = st.selectbox(
        "Choose a certificate to revoke:",
        range(len(active_certificates)),
        format_func=lambda i: cert_options[i],
        key="cert_select"
    )
    
    selected_cert = active_certificates[selected_option]
    
    st.divider()
    
    # Certificate Details Section
    st.subheader(" Certificate Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Certificate ID:** {selected_cert.id}")
        st.write(f"**Request ID:** {selected_cert.request_id if selected_cert.request_id else 'N/A'}")
        st.write(f"**User ID:** {selected_cert.user_id}")
        st.write(f"**Serial Number:** `{selected_cert.serial_number}`")
    
    with col2:
        st.write(f"**Status:** {selected_cert.status.value}")
        st.write(f"**Valid From:** {selected_cert.valid_from.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Valid To:** {selected_cert.valid_to.strftime('%Y-%m-%d %H:%M:%S')}")
        remaining_days = (selected_cert.valid_to - datetime.now()).days
        st.write(f"**Days Remaining:** {remaining_days} day(s)")
    
    # Certificate PEM
    with st.expander("📄 View Certificate PEM"):
        st.markdown(f"""
        <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
        <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{selected_cert.cert_pem}</pre>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Revocation Reason Section
    st.subheader(" Revocation Reason")
    
    revocation_reason = st.selectbox(
        "Select revocation reason:",
        [
            "Key Compromise",
            "CA Compromise",
            "Affiliation Changed",
            "Superseded",
            "Cessation of Operation",
            "Certificate Hold",
            "Remove from CRL",
            "Privilege Withdrawn",
            "AA Compromise",
            "Other"
        ],
        help="Select the reason for revoking this certificate"
    )
    
    additional_details = st.text_area(
        "Additional Details (Optional)",
        placeholder="Enter any additional information about this revocation...",
        height=100,
        help="Provide additional context for the revocation"
    )
    
    
    # Revocation Warning
    st.warning(
        f"⚠️ **Warning:** This action will immediately revoke certificate #{selected_cert.id}. "
        f"This certificate will no longer be valid and cannot be undone. "
        f"Users depending on this certificate will be affected.",
        icon="⚠️"
    )
   
    # Revocation Action Section
    st.subheader(" Confirm Revocation")
    
    # Confirmation checkbox
    confirm = st.checkbox(
        "I confirm I want to revoke this certificate",
        help="Check this box to enable the revoke button"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(
            "🚫 Revoke Certificate",
            use_container_width=True,
            type="primary",
            disabled=not confirm
        ):
            if not confirm:
                st.error("❌ Please confirm before revoking the certificate")
            else:
                # Store revocation data
                revocation_record = {
                    "cert_id": selected_cert.id,
                    "user_id": selected_cert.user_id,
                    "serial_number": selected_cert.serial_number,
                    "reason": revocation_reason,
                    "details": additional_details,
                    "revoked_at": datetime.now()
                }
                st.session_state.revoked_certs.append(revocation_record)
                
                # Display success message
                st.success(
                    f"✅ Certificate #{selected_cert.id} revoked successfully!\n\n"
                    f"**Details:**\n"
                    f"- User ID: {selected_cert.user_id}\n"
                    f"- Serial Number: {selected_cert.serial_number}\n"
                    f"- Revocation Reason: {revocation_reason}\n"
                    f"- Revoked At: {revocation_record['revoked_at'].strftime('%Y-%m-%d %H:%M:%S')}",
                    icon="✅"
                )
                
                st.info(
                    "📌 The certificate has been added to the Certificate Revocation List (CRL) "
                    "and will be published in the next CRL update.",
                    icon="ℹ️"
                )
    
    st.divider()
    
    # Summary Section
    st.subheader(" Revocation Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Selection:**")
        st.write(f"- Certificate ID: {selected_cert.id}")
        st.write(f"- Serial Number: {selected_cert.serial_number}")
        st.write(f"- Reason: {revocation_reason}")
    
    with col2:
        st.write("**Previously Revoked:**")
        if st.session_state.revoked_certs:
            for idx, revoked in enumerate(st.session_state.revoked_certs, 1):
                st.write(f"- Cert #{revoked['cert_id']} ({revoked['reason']}) ✅")
        else:
            st.write("- None yet")
    
    st.divider()
    
    # Display statistics at bottom
    st.subheader("📊 Revocation Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Active", len(active_certificates))
    with col2:
        st.metric("🚫 Revoked", len([c for c in all_certificates if c.status == CertStatus.REVOKED]))
    with col3:
        st.metric("⏰ Expired", len([c for c in all_certificates if c.status == CertStatus.EXPIRED]))
    with col4:
        st.metric("📋 Total", len(all_certificates))
    st.divider()
