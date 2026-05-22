import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# Enums
class CertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"

# Mock Data Model
@dataclass
class CertificateOut:
    id: int
    user_id: int
    serial_number: str
    subject_dn: str
    cert_pem: str
    status: CertStatus
    valid_from: datetime
    valid_to: datetime
    created_at: datetime

# Mock Data Generator
def get_mock_expiring_certificates() -> List[CertificateOut]:
    """Generate mock expiring certificate data"""
    return [
        CertificateOut(
            id=1,
            user_id=5,
            serial_number="01:A2:B3:C4:D5:E6:F7:08",
            subject_dn="CN=user1@example.com,O=Organization,C=US",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.EXPIRING_SOON,
            valid_from=datetime.now() - timedelta(days=350),
            valid_to=datetime.now() + timedelta(days=15),
            created_at=datetime.now() - timedelta(days=350)
        ),
        CertificateOut(
            id=2,
            user_id=6,
            serial_number="02:B3:C4:D5:E6:F7:08:09",
            subject_dn="CN=user2@example.com,O=Organization,C=US",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.EXPIRING_SOON,
            valid_from=datetime.now() - timedelta(days=360),
            valid_to=datetime.now() + timedelta(days=5),
            created_at=datetime.now() - timedelta(days=360)
        ),
        CertificateOut(
            id=3,
            user_id=7,
            serial_number="03:C4:D5:E6:F7:08:09:0A",
            subject_dn="CN=user3@example.com,O=Organization,C=US",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.EXPIRING_SOON,
            valid_from=datetime.now() - timedelta(days=340),
            valid_to=datetime.now() + timedelta(days=25),
            created_at=datetime.now() - timedelta(days=340)
        ),
        CertificateOut(
            id=4,
            user_id=8,
            serial_number="04:D5:E6:F7:08:09:0A:0B",
            subject_dn="CN=service@example.com,O=Organization,C=US",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.EXPIRING_SOON,
            valid_from=datetime.now() - timedelta(days=355),
            valid_to=datetime.now() + timedelta(days=10),
            created_at=datetime.now() - timedelta(days=355)
        ),
        CertificateOut(
            id=5,
            user_id=9,
            serial_number="05:E6:F7:08:09:0A:0B:0C",
            subject_dn="CN=admin@example.com,O=Organization,C=US",
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\nMIIDXTCCAkWgAwIBAgIJAKZ1234567890AB\n-----END CERTIFICATE-----",
            status=CertStatus.EXPIRED,
            valid_from=datetime.now() - timedelta(days=370),
            valid_to=datetime.now() - timedelta(days=10),
            created_at=datetime.now() - timedelta(days=370)
        ),
    ]

def renew_certificates():
    
    # Initialize session state
    if "renewed_certificates" not in st.session_state:
        st.session_state.renewed_certificates = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Renew Certificates")
    st.markdown("Renew expiring or expired certificates for users")
    
    st.divider()
    
    # Get mock data
    all_certificates = get_mock_expiring_certificates()
    expiring_soon = [c for c in all_certificates if c.status == CertStatus.EXPIRING_SOON]
    expired = [c for c in all_certificates if c.status == CertStatus.EXPIRED]
    
    
    
    # Create tabs
    tab1, tab2 = st.tabs([" Renew Certificate", " Renewal History"])
    
    with tab1:
        st.subheader("Select Certificate to Renew")
        
        # Certificate selection
        cert_options = [
            f"Cert #{c.id} - {c.subject_dn} - Expires in {(c.valid_to - datetime.now()).days}d"
            for c in all_certificates
        ]
        
        selected_idx = st.selectbox(
            "Choose a certificate to renew:",
            range(len(all_certificates)),
            format_func=lambda i: cert_options[i],
            key="renew_cert_select"
        )
        
        selected_cert = all_certificates[selected_idx]
        
        st.divider()
        
        # Current Certificate Details
        st.subheader("Current Certificate Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Certificate ID:** {selected_cert.id}")
            st.write(f"**User ID:** {selected_cert.user_id}")
            st.write(f"**Serial Number:** `{selected_cert.serial_number}`")
            st.write(f"**Subject:** `{selected_cert.subject_dn}`")
        
        with col2:
            st.write(f"**Valid From:** {selected_cert.valid_from.strftime('%Y-%m-%d')}")
            st.write(f"**Valid To:** {selected_cert.valid_to.strftime('%Y-%m-%d')}")
            st.write(f"**Status:** {selected_cert.status.value}")
            
            now = datetime.now()
            if selected_cert.valid_to < now:
                days_expired = (now - selected_cert.valid_to).days
                st.write(f"**Expired:** {days_expired} day(s) ago")
            else:
                days_left = (selected_cert.valid_to - now).days
                st.write(f"**Days Until Expiry:** {days_left} day(s)")
        
        
        # Current Certificate PEM
        st.markdown("**📄 Current Certificate (PEM):**")
        st.markdown(f"""
        <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto; max-height: 150px;">
        <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{selected_cert.cert_pem}</pre>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Renewal Configuration
        st.subheader(" Renewal Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            validity_days = st.number_input(
                "New Validity Period (days):",
                min_value=365,
                max_value=3650,
                value=365,
                step=365,
                key="renew_validity_days"
            )
            
            st.markdown(f"""
            **New Validity:**
            - Valid From: {datetime.now().strftime('%Y-%m-%d')}
            - Valid To: {(datetime.now() + timedelta(days=validity_days)).strftime('%Y-%m-%d')}
            - Duration: {validity_days} days (~{validity_days/365:.1f} years)
            """)
        
        with col2:
            hash_algorithm = st.selectbox(
                "Hash Algorithm:",
                options=["SHA256", "SHA384", "SHA512"],
                index=0,
                key="renew_hash_algorithm"
            )
            
            key_size = st.selectbox(
                "Key Size (bits):",
                options=[2048, 3072, 4096],
                index=0,
                key="renew_key_size"
            )
            
            keep_key = st.checkbox(
                "Keep existing private key",
                value=False,
                key="renew_keep_key"
            )
        
      
        # Renewal Information
        with st.expander("ℹ️ Certificate Renewal Information"):
            st.markdown("""
            **Certificate Renewal Process:**
            1. New certificate will be generated with same subject DN
            2. Old certificate remains valid until expiry
            3. Both certificates can be used until old one expires
            4. Update applications to use new certificate
            5. Old certificate should be removed after full transition
            
            **Key Considerations:**
            - New certificate gets different serial number
            - Certificate chain may need updating
            - Update any OCSP/CRL references
            - Notify users of certificate change
            """)
        
        # Renewal Summary
        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #9f7aea; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #9f7aea; margin-bottom: 10px;">🔄 Renewal Summary</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> Subject: <strong>{selected_cert.subject_dn}</strong></div>
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> New validity: <strong>{validity_days} days</strong></div>
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> Hash algorithm: <strong>{hash_algorithm}</strong></div>
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> Key size: <strong>{key_size} bits</strong></div>
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">{'✅' if keep_key else '🔄'}</span> Private key: <strong>{'Reused' if keep_key else 'Regenerated'}</strong></div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Confirmation and Renewal
        confirm_renew = st.checkbox(
            "I confirm the certificate renewal",
            key="confirm_renew_cert"
        )
        
        if st.button(
            "🔄 Renew Certificate",
            disabled=not confirm_renew,
            key="btn_renew_cert",
            use_container_width=True
        ):
            # Simulate renewal
            with st.spinner("Renewing certificate..."):
                import time
                time.sleep(2)
                
                # Store in session
                new_renewal = {
                    "original_cert_id": selected_cert.id,
                    "new_cert_id": selected_cert.id + 100,
                    "user_id": selected_cert.user_id,
                    "subject_dn": selected_cert.subject_dn,
                    "old_valid_to": selected_cert.valid_to,
                    "new_valid_to": datetime.now() + timedelta(days=validity_days),
                    "hash_algorithm": hash_algorithm,
                    "key_size": key_size,
                    "timestamp": datetime.now()
                }
                st.session_state.renewed_certificates.append(new_renewal)
                
                st.success(f"""
                ✅ Certificate Renewed Successfully!
                
                **Renewal Details:**
                - **Original Certificate ID:** {selected_cert.id}
                - **New Certificate ID:** {selected_cert.id + 100}
                - **Subject:** {selected_cert.subject_dn}
                - **New Serial Number:** {selected_cert.id + 100:02X}:A2:B3:C4:D5:E6:F7:08
                - **Valid From:** {datetime.now().strftime('%Y-%m-%d')}
                - **Valid To:** {(datetime.now() + timedelta(days=validity_days)).strftime('%Y-%m-%d')}
                - **Hash Algorithm:** {hash_algorithm}
                - **Renewed At:** {new_renewal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                
                **⚠️ Next Steps:**
                1. Download the new certificate
                2. Update applications to use the new certificate
                3. Monitor the transition period
                4. Revoke old certificate after transition (optional)
                """)
                
                # New Certificate PEM
                st.markdown("**📄 New Certificate (PEM):**")
                new_cert_pem = f"""-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJ{selected_cert.id + 100:04X}9AB
MIIDXTCCAkWgAwIBAgIJAKZ1234567890AB
-----END CERTIFICATE-----"""
                
                st.text_area(
                    "New Certificate Content",
                    value=new_cert_pem,
                    height=150,
                    disabled=True,
                    key="new_cert_pem_display"
                )
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Download Certificate", key="download_renewed_cert"):
                        st.info("Certificate downloaded successfully")
                
                with col2:
                    if st.button("📋 Copy PEM", key="copy_renewed_cert_pem"):
                        st.success("Certificate PEM copied to clipboard!")
    
    with tab2:
        st.subheader("Certificate Renewal History")
        
        if not st.session_state.renewed_certificates:
            st.info("No certificate renewals yet.")
        else:
            # Renewal history table
            history_data = []
            for renewal in st.session_state.renewed_certificates:
                history_data.append({
                    "Original ID": renewal['original_cert_id'],
                    "New ID": renewal['new_cert_id'],
                    "User ID": renewal['user_id'],
                    "Subject": renewal['subject_dn'],
                    "New Valid To": renewal['new_valid_to'].strftime('%Y-%m-%d'),
                    "Algorithm": renewal['hash_algorithm'],
                    "Renewed": renewal['timestamp'].strftime('%Y-%m-%d %H:%M')
                })
            
            df_history = pd.DataFrame(history_data)
            st.dataframe(
                df_history,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Original ID": st.column_config.NumberColumn(width="small"),
                    "New ID": st.column_config.NumberColumn(width="small"),
                    "User ID": st.column_config.NumberColumn(width="small"),
                    "Subject": st.column_config.TextColumn(width="large"),
                    "New Valid To": st.column_config.TextColumn(width="medium"),
                    "Algorithm": st.column_config.TextColumn(width="medium"),
                    "Renewed": st.column_config.TextColumn(width="medium")
                }
            )
            
            st.divider()
            
            # Renewal details
            st.markdown("**Recent Renewals**")
            
            for renewal in reversed(st.session_state.renewed_certificates[-3:]):
                with st.expander(f"Cert #{renewal['original_cert_id']} → #{renewal['new_cert_id']} - {renewal['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**User ID:** {renewal['user_id']}")
                        st.write(f"**Subject:** {renewal['subject_dn']}")
                        st.write(f"**Old Valid To:** {renewal['old_valid_to'].strftime('%Y-%m-%d')}")
                    
                    with col2:
                        st.write(f"**New Valid To:** {renewal['new_valid_to'].strftime('%Y-%m-%d')}")
                        st.write(f"**Hash Algorithm:** {renewal['hash_algorithm']}")
                        st.write(f"**Key Size:** {renewal['key_size']} bits")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📥 Download", key=f"download_renewal_{renewal['new_cert_id']}"):
                            st.info(f"Certificate #{renewal['new_cert_id']} downloaded")
                    
                    with col2:
                        if st.button("❌ Revoke Old", key=f"revoke_old_{renewal['original_cert_id']}"):
                            st.warning(f"Certificate #{renewal['original_cert_id']} revocation initiated")
    st.divider()

    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏰ Expiring Soon", len(expiring_soon))
    with col2:
        st.metric("❌ Expired", len(expired))
    with col3:
        st.metric("🔄 Total to Renew", len(all_certificates))
    with col4:
        st.metric("✅ Renewed", len(st.session_state.renewed_certificates))
    
    st.divider()
