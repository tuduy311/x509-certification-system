import streamlit as st
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass

# Mock Data Model
@dataclass
class CertificateOut:
    id: int
    serial_number: str
    subject_dn: str
    status: str
    valid_from: datetime
    valid_to: datetime

def get_mock_expiring_certificates() -> List[CertificateOut]:
    """Get user's expiring certificates"""
    return [
        CertificateOut(
            id=1,
            serial_number="01:A2:B3:C4:D5:E6:F7:08",
            subject_dn="CN=user@example.com,O=MyOrg,C=US",
            status="EXPIRING_SOON",
            valid_from=datetime.now() - timedelta(days=350),
            valid_to=datetime.now() + timedelta(days=15)
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

def renew_certificate():
    
    # Initialize session state
    if "renewed_certificates" not in st.session_state:
        st.session_state.renewed_certificates = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title("🔄 Renew Certificate")
    st.markdown("Renew your expiring or expired certificates")
    
    st.divider()
    
    # Create tabs
    tab1, tab2 = st.tabs(["📝 Renew Certificate", "📊 Renewal History"])
    
    with tab1:
        st.subheader("Select Certificate to Renew")
        
        expiring_certs = get_mock_expiring_certificates()
        
        if not expiring_certs:
            st.warning("⚠️ No expiring certificates available to renew.")
        else:
            # Certificate selection
            cert_options = [f"Cert #{c.id} - {c.subject_dn} (Expires: {(c.valid_to - datetime.now()).days}d)" for c in expiring_certs]
            selected_idx = st.selectbox(
                "Select certificate to renew:",
                range(len(expiring_certs)),
                format_func=lambda i: cert_options[i],
                key="cert_to_renew"
            )
            
            selected_cert = expiring_certs[selected_idx]
            
            st.divider()
            
            # Certificate details
            st.markdown("**📄 Current Certificate Details:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**ID:** {selected_cert.id}")
                st.write(f"**Serial Number:** `{selected_cert.serial_number}`")
                st.write(f"**Subject:** `{selected_cert.subject_dn}`")
            
            with col2:
                st.write(f"**Valid From:** {selected_cert.valid_from.strftime('%Y-%m-%d')}")
                st.write(f"**Valid To:** {selected_cert.valid_to.strftime('%Y-%m-%d')}")
                days_left = (selected_cert.valid_to - datetime.now()).days
                st.write(f"**Days Left:** {days_left} days")
            
            st.divider()
            
            # Renewal configuration
            st.markdown("**⚙️ Renewal Configuration:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                validity_period = st.number_input(
                    "Validity Period (days):",
                    min_value=30,
                    max_value=3650,
                    value=365,
                    step=30,
                    key="renew_validity"
                )
                
                hash_algo = st.selectbox(
                    "Hash Algorithm:",
                    ["SHA-256", "SHA-384", "SHA-512"],
                    key="renew_hash"
                )
            
            with col2:
                key_size = st.selectbox(
                    "Key Size:",
                    ["2048", "3072", "4096"],
                    key="renew_keysize"
                )
                
                csr_required = st.checkbox(
                    "Use existing CSR",
                    value=False,
                    key="renew_use_csr"
                )
            
            if csr_required:
                st.markdown("**📝 Provide CSR:**")
                csr_pem = st.text_area(
                    "CSR in PEM format:",
                    placeholder="-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
                    height=100,
                    key="renew_csr"
                )
            
            st.divider()
            
            # Renewal summary
            new_expiry = datetime.now() + timedelta(days=validity_period)
            
            st.markdown(f"""
            <div style="background-color: #2d3748; border-left: 4px solid #4299e1; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="font-weight: bold; color: #4299e1; margin-bottom: 10px;">🔄 Renewal Summary</div>
            <div style="color: #e0e0e0; font-size: 14px;">
            <div style="margin: 5px 0;"><strong>Certificate ID:</strong> {selected_cert.id}</div>
            <div style="margin: 5px 0;"><strong>Serial Number:</strong> {selected_cert.serial_number}</div>
            <div style="margin: 5px 0;"><strong>New Validity:</strong> {validity_period} days</div>
            <div style="margin: 5px 0;"><strong>New Expiry Date:</strong> {new_expiry.strftime('%Y-%m-%d')}</div>
            <div style="margin: 5px 0;"><strong>Hash Algorithm:</strong> {hash_algo}</div>
            <div style="margin: 5px 0;"><strong>Key Size:</strong> {key_size} bits</div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            confirm = st.checkbox(
                "✓ I confirm this certificate renewal",
                key="confirm_renew"
            )
            
            if st.button(
                "🔄 Renew Certificate",
                disabled=not confirm,
                key="btn_renew",
                use_container_width=True
            ):
                new_renewal = {
                    "id": len(st.session_state.renewed_certificates) + 1,
                    "cert_id": selected_cert.id,
                    "serial_number": selected_cert.serial_number,
                    "validity": validity_period,
                    "expiry": new_expiry,
                    "timestamp": datetime.now()
                }
                st.session_state.renewed_certificates.append(new_renewal)
                
                with st.spinner("Processing renewal..."):
                    import time
                    time.sleep(2)
                
                st.success(f"""
                ✅ Certificate Renewed Successfully!
                
                **Renewal Details:**
                - **Certificate ID:** {selected_cert.id}
                - **New Validity:** {validity_period} days
                - **New Expiry:** {new_expiry.strftime('%Y-%m-%d %H:%M:%S')}
                - **Hash Algorithm:** {hash_algo}
                - **Renewed:** {new_renewal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                
                Your certificate has been renewed and is ready to use.
                """)
    
    with tab2:
        st.subheader("Renewal History")
        
        if not st.session_state.renewed_certificates:
            st.info("No certificate renewals yet.")
        else:
            for renewal in st.session_state.renewed_certificates:
                with st.expander(f"🔄 Renewal #{renewal['id']} - Cert #{renewal['cert_id']} ({renewal['timestamp'].strftime('%Y-%m-%d')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Renewal ID:** {renewal['id']}")
                        st.write(f"**Certificate ID:** {renewal['cert_id']}")
                        st.write(f"**Serial Number:** {renewal['serial_number']}")
                    
                    with col2:
                        st.write(f"**Validity:** {renewal['validity']} days")
                        st.write(f"**New Expiry:** {renewal['expiry'].strftime('%Y-%m-%d')}")
                        st.write(f"**Renewed:** {renewal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.divider()
    
    # Statistics
    st.subheader("📊 Renewal Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔄 Total Renewals", len(st.session_state.renewed_certificates))
    with col2:
        st.metric("⏰ Expiring Soon", len(expiring_certs))
    with col3:
        st.metric("✅ Active", len([c for c in expiring_certs if c.status == "ACTIVE"]))
