import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# Enums
class CertStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"

# Mock Data Models
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

@dataclass
class RevocationRequestOut:
    id: int
    certificate_id: int
    user_id: int
    reason: str
    status: CertStatus
    created_at: datetime

# Mock Data Generators
def get_mock_issued_certificates() -> List[CertificateOut]:
    """Generate mock issued certificate data"""
    return [
        CertificateOut(
            id=1,
            request_id=1,
            user_id=5,
            serial_number="01:A2:B3:C4:D5:E6:F7:08",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=30),
            valid_to=datetime.now() + timedelta(days=335),
            created_at=datetime.now() - timedelta(days=30)
        ),
        CertificateOut(
            id=2,
            request_id=2,
            user_id=6,
            serial_number="02:B3:C4:D5:E6:F7:08:09",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=100),
            valid_to=datetime.now() + timedelta(days=265),
            created_at=datetime.now() - timedelta(days=100)
        ),
        CertificateOut(
            id=3,
            request_id=3,
            user_id=7,
            serial_number="03:C4:D5:E6:F7:08:09:0A",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=200),
            valid_to=datetime.now() + timedelta(days=165),
            created_at=datetime.now() - timedelta(days=200)
        ),
        CertificateOut(
            id=4,
            request_id=4,
            user_id=8,
            serial_number="04:D5:E6:F7:08:09:0A:0B",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.REVOKED,
            valid_from=datetime.now() - timedelta(days=300),
            valid_to=datetime.now() - timedelta(days=50),
            created_at=datetime.now() - timedelta(days=300)
        ),
        CertificateOut(
            id=5,
            request_id=5,
            user_id=9,
            serial_number="05:E6:F7:08:09:0A:0B:0C",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.EXPIRED,
            valid_from=datetime.now() - timedelta(days=400),
            valid_to=datetime.now() - timedelta(days=35),
            created_at=datetime.now() - timedelta(days=400)
        ),
        CertificateOut(
            id=6,
            request_id=6,
            user_id=10,
            serial_number="06:F7:08:09:0A:0B:0C:0D",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=10),
            valid_to=datetime.now() + timedelta(days=355),
            created_at=datetime.now() - timedelta(days=10)
        ),
    ]

def get_mock_revocation_requests() -> List[RevocationRequestOut]:
    """Generate mock revocation request data"""
    return [
        RevocationRequestOut(
            id=1,
            certificate_id=4,
            user_id=8,
            reason="Key compromise",
            status=CertStatus.REVOKED,
            created_at=datetime.now() - timedelta(days=50)
        ),
        RevocationRequestOut(
            id=2,
            certificate_id=3,
            user_id=7,
            reason="Cessation of operation",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(days=2)
        ),
    ]

def issued_certificates():
    
    # Initialize session state
    if "revocation_requests" not in st.session_state:
        st.session_state.revocation_requests = []
    
    # Back to Dashboard Button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    # Header Section
    st.title(" Issued Certificates")
    st.markdown("View and manage all issued X.509 certificates")
    
    st.divider()
    
    # Get mock data
    all_certificates = get_mock_issued_certificates()
    revocation_requests = get_mock_revocation_requests()
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Active", len([c for c in all_certificates if c.status == CertStatus.ACTIVE]))
    with col2:
        st.metric("❌ Revoked", len([c for c in all_certificates if c.status == CertStatus.REVOKED]))
    with col3:
        st.metric("⏰ Expired", len([c for c in all_certificates if c.status == CertStatus.EXPIRED]))
    with col4:
        st.metric("📊 Total", len(all_certificates))
    
    st.divider()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([" All Certificates", " Details", " Revocation Requests"])
    
    with tab1:
        st.subheader("Issued Certificates List")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect(
                "Filter by Status:",
                options=[CertStatus.ACTIVE.value, CertStatus.REVOKED.value, CertStatus.EXPIRED.value],
                default=[CertStatus.ACTIVE.value, CertStatus.REVOKED.value, CertStatus.EXPIRED.value],
                key="cert_status_filter"
            )
        
        with col2:
            search_user = st.text_input(
                "Search by User ID:",
                value="",
                key="cert_search_user"
            )
        
        with col3:
            search_serial = st.text_input(
                "Search by Serial Number:",
                value="",
                key="cert_search_serial"
            )
        
        # Filter certificates
        filtered_certs = all_certificates
        
        if status_filter:
            filtered_certs = [c for c in filtered_certs if c.status.value in status_filter]
        
        if search_user:
            filtered_certs = [c for c in filtered_certs if str(c.user_id) == search_user]
        
        if search_serial:
            filtered_certs = [c for c in filtered_certs if search_serial.lower() in c.serial_number.lower()]
        
        # Create DataFrame
        cert_data = []
        for cert in filtered_certs:
            now = datetime.now()
            if cert.status == CertStatus.ACTIVE:
                validity = f"✅ {(cert.valid_to - now).days}d left"
            elif cert.status == CertStatus.REVOKED:
                validity = "❌ Revoked"
            else:
                validity = "⏰ Expired"
            
            cert_data.append({
                "ID": cert.id,
                "Serial Number": cert.serial_number,
                "User ID": cert.user_id,
                "Status": cert.status.value,
                "Valid From": cert.valid_from.strftime('%Y-%m-%d'),
                "Valid To": cert.valid_to.strftime('%Y-%m-%d'),
                "Validity": validity
            })
        
        df = pd.DataFrame(cert_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn(width="small"),
                "Serial Number": st.column_config.TextColumn(width="large"),
                "User ID": st.column_config.NumberColumn(width="small"),
                "Status": st.column_config.TextColumn(width="medium"),
                "Valid From": st.column_config.TextColumn(width="medium"),
                "Valid To": st.column_config.TextColumn(width="medium"),
                "Validity": st.column_config.TextColumn(width="medium")
            }
        )
        
        st.info(f"📊 Showing {len(cert_data)} of {len(all_certificates)} certificates")
    
    with tab2:
        st.subheader("Certificate Details")
        
        # Select certificate
        cert_options = [f"Cert #{c.id} - User {c.user_id} - {c.status.value}" for c in all_certificates]
        selected_idx = st.selectbox(
            "Select a certificate to view details:",
            range(len(all_certificates)),
            format_func=lambda i: cert_options[i],
            key="cert_detail_select"
        )
        
        selected_cert = all_certificates[selected_idx]
        
        st.divider()
        
        # Certificate details
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Certificate ID:** {selected_cert.id}")
            st.write(f"**Serial Number:** `{selected_cert.serial_number}`")
            st.write(f"**User ID:** {selected_cert.user_id}")
            st.write(f"**Request ID:** {selected_cert.request_id}")
            st.write(f"**Status:** {selected_cert.status.value}")
        
        with col2:
            st.write(f"**Created:** {selected_cert.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Valid From:** {selected_cert.valid_from.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Valid To:** {selected_cert.valid_to.strftime('%Y-%m-%d %H:%M:%S')}")
            
            now = datetime.now()
            if selected_cert.status == CertStatus.ACTIVE:
                days_left = (selected_cert.valid_to - now).days
                st.write(f"**Days Until Expiry:** {days_left} days")
            elif selected_cert.status == CertStatus.EXPIRED:
                days_expired = (now - selected_cert.valid_to).days
                st.write(f"**Days Since Expiry:** {days_expired} days")
        
        st.divider()
        
        # Certificate PEM
        st.markdown("**📄 Certificate (PEM):**")
        st.markdown(f"""
        <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
        <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{selected_cert.cert_pem}</pre>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📥 Download", key=f"download_cert_{selected_cert.id}"):
                st.success(f"Certificate #{selected_cert.id} downloaded")
        
        with col2:
            if st.button("📋 Copy PEM", key=f"copy_cert_{selected_cert.id}"):
                st.success("Certificate PEM copied to clipboard!")
        
        with col3:
            if st.button("🔍 Verify", key=f"verify_cert_{selected_cert.id}"):
                st.info("Certificate verification initiated")
        
        with col4:
            if selected_cert.status == CertStatus.ACTIVE and st.button("❌ Revoke", key=f"revoke_cert_{selected_cert.id}"):
                st.warning(f"Revocation request for Certificate #{selected_cert.id} created")
    
    with tab3:
        st.subheader("Revocation Requests")
        
        if not revocation_requests:
            st.info("No revocation requests found.")
        else:
            # Revocation requests table
            revoke_data = []
            for rev_req in revocation_requests:
                revoke_data.append({
                    "Request ID": rev_req.id,
                    "Certificate ID": rev_req.certificate_id,
                    "User ID": rev_req.user_id,
                    "Reason": rev_req.reason,
                    "Status": rev_req.status.value,
                    "Created": rev_req.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            df_revoke = pd.DataFrame(revoke_data)
            st.dataframe(
                df_revoke,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Request ID": st.column_config.NumberColumn(width="small"),
                    "Certificate ID": st.column_config.NumberColumn(width="small"),
                    "User ID": st.column_config.NumberColumn(width="small"),
                    "Reason": st.column_config.TextColumn(width="large"),
                    "Status": st.column_config.TextColumn(width="medium"),
                    "Created": st.column_config.TextColumn(width="medium")
                }
            )
            
            st.divider()
            
            # Pending revocation requests
            pending_revokes = [r for r in revocation_requests if r.status == CertStatus.PENDING]
            
            if pending_revokes:
                st.markdown("**⏳ Pending Revocation Requests**")
                
                for rev_req in pending_revokes:
                    with st.expander(f"Request #{rev_req.id} - Certificate #{rev_req.certificate_id}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**User ID:** {rev_req.user_id}")
                            st.write(f"**Reason:** {rev_req.reason}")
                        
                        with col2:
                            st.write(f"**Requested:** {rev_req.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                            st.write(f"**Status:** {rev_req.status.value}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Approve", key=f"approve_revoke_{rev_req.id}"):
                                st.success(f"Revocation request #{rev_req.id} approved")
                        
                        with col2:
                            if st.button("❌ Reject", key=f"reject_revoke_{rev_req.id}"):
                                st.error(f"Revocation request #{rev_req.id} rejected")
