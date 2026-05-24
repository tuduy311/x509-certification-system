import streamlit as st
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# Enums
class CertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"

# Mock Data Model
@dataclass
class CertificateOut:
    id: int
    serial_number: str
    subject_dn: str
    cert_pem: str
    status: CertStatus
    valid_from: datetime
    valid_to: datetime
    created_at: datetime

# Mock Data Generator
def get_mock_user_certificates() -> List[CertificateOut]:
    """Generate mock certificates for current user"""
    return [
        CertificateOut(
            id=1,
            serial_number="01:A2:B3:C4:D5:E6:F7:08",
            subject_dn="CN=user@example.com,O=MyOrg,C=US",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=30),
            valid_to=datetime.now() + timedelta(days=335),
            created_at=datetime.now() - timedelta(days=30)
        ),
        CertificateOut(
            id=2,
            serial_number="02:B3:C4:D5:E6:F7:08:09",
            subject_dn="CN=user@example.com,O=MyOrg,C=US",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.ACTIVE,
            valid_from=datetime.now() - timedelta(days=100),
            valid_to=datetime.now() + timedelta(days=265),
            created_at=datetime.now() - timedelta(days=100)
        ),
        CertificateOut(
            id=3,
            serial_number="03:C4:D5:E6:F7:08:09:0A",
            subject_dn="CN=user@example.com,O=MyOrg,C=US",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.EXPIRED,
            valid_from=datetime.now() - timedelta(days=400),
            valid_to=datetime.now() - timedelta(days=35),
            created_at=datetime.now() - timedelta(days=400)
        ),
    ]

def my_certificates():
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" My Certificates")
    st.markdown("View and manage your X.509 certificates")
    
    st.divider()
    
    # Get mock data
    all_certs = get_mock_user_certificates()
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Active", len([c for c in all_certs if c.status == CertStatus.ACTIVE]))
    with col2:
        st.metric("⏰ Expired", len([c for c in all_certs if c.status == CertStatus.EXPIRED]))
    with col3:
        st.metric("📊 Total", len(all_certs))
    
    st.divider()
    
    # Create tabs
    tab1, tab2 = st.tabs([" All Certificates", " Details"])
    
    with tab1:
        st.subheader("My Certificates")
        
        if not all_certs:
            st.info("You don't have any certificates yet.")
        else:
            # Create DataFrame
            cert_data = []
            for cert in all_certs:
                now = datetime.now()
                if cert.status == CertStatus.ACTIVE:
                    validity = f"✅ {(cert.valid_to - now).days}d left"
                elif cert.status == CertStatus.EXPIRED:
                    validity = "⏰ Expired"
                else:
                    validity = "❌ Revoked"
                
                cert_data.append({
                    "ID": cert.id,
                    "Serial Number": cert.serial_number,
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
                    "Status": st.column_config.TextColumn(width="medium"),
                    "Valid From": st.column_config.TextColumn(width="medium"),
                    "Valid To": st.column_config.TextColumn(width="medium"),
                    "Validity": st.column_config.TextColumn(width="medium")
                }
            )
    
    with tab2:
        st.subheader("Certificate Details")
        
        # Select certificate
        cert_options = [f"Cert #{c.id} - {c.status.value}" for c in all_certs]
        selected_idx = st.selectbox(
            "Select a certificate to view details:",
            range(len(all_certs)),
            format_func=lambda i: cert_options[i],
            key="cert_detail_select"
        )
        
        selected_cert = all_certs[selected_idx]
        
        st.divider()
        
        # Certificate details
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Certificate ID:** {selected_cert.id}")
            st.write(f"**Serial Number:** `{selected_cert.serial_number}`")
            st.write(f"**Subject:** `{selected_cert.subject_dn}`")
            st.write(f"**Status:** {selected_cert.status.value}")
        
        with col2:
            st.write(f"**Created:** {selected_cert.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Valid From:** {selected_cert.valid_from.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Valid To:** {selected_cert.valid_to.strftime('%Y-%m-%d %H:%M:%S')}")
            
            now = datetime.now()
            if selected_cert.status == CertStatus.ACTIVE:
                days_left = (selected_cert.valid_to - now).days
                st.write(f"**Days Until Expiry:** {days_left} days")
        
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
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download", key=f"download_cert_{selected_cert.id}"):
                st.success(f"Certificate #{selected_cert.id} downloaded")
        
        with col2:
            if st.button("📋 Copy PEM", key=f"copy_cert_{selected_cert.id}"):
                st.success("Certificate PEM copied to clipboard!")
        
        with col3:
            if selected_cert.status == CertStatus.ACTIVE and st.button("🔄 Renew", key=f"renew_cert_{selected_cert.id}"):
                st.session_state.current_feature = "my_request_status"
                st.rerun()
