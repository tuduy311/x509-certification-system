import streamlit as st
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import List
import pandas as pd

# Enums
class CertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"

# Mock Data Model
@dataclass
class RevokedCertificateOut:
    certificate_id: int
    serial_number: str
    subject_dn: str
    status: CertStatus
    revoked_at: datetime
    revocation_reason: str

# Mock Data Generator
def get_mock_revoked_certificates() -> List[RevokedCertificateOut]:
    """Generate mock revoked certificate records"""
    return [
        RevokedCertificateOut(
            certificate_id=1,
            serial_number="01:A2:B3:C4:D5:E6:F7:08",
            subject_dn="CN=user@example.com,O=Organization,C=US",
            status=CertStatus.REVOKED,
            revoked_at=datetime.now() - timedelta(days=5),
            revocation_reason="Superseded"
        ),
        RevokedCertificateOut(
            certificate_id=2,
            serial_number="02:B3:C4:D5:E6:F7:08:09",
            subject_dn="CN=admin@example.com,O=Organization,C=US",
            status=CertStatus.REVOKED,
            revoked_at=datetime.now() - timedelta(days=3),
            revocation_reason="Key Compromise"
        ),
        RevokedCertificateOut(
            certificate_id=3,
            serial_number="03:C4:D5:E6:F7:08:09:0A",
            subject_dn="CN=service@example.com,O=Organization,C=US",
            status=CertStatus.REVOKED,
            revoked_at=datetime.now() - timedelta(days=10),
            revocation_reason="CA Compromise"
        ),
        RevokedCertificateOut(
            certificate_id=4,
            serial_number="04:D5:E6:F7:08:09:0A:0B",
            subject_dn="CN=test@example.com,O=Organization,C=US",
            status=CertStatus.REVOKED,
            revoked_at=datetime.now() - timedelta(days=1),
            revocation_reason="Cessation of Operation"
        ),
        RevokedCertificateOut(
            certificate_id=5,
            serial_number="05:E6:F7:08:09:0A:0B:0C",
            subject_dn="CN=old@example.com,O=Organization,C=US",
            status=CertStatus.REVOKED,
            revoked_at=datetime.now() - timedelta(days=15),
            revocation_reason="Superseded"
        ),
    ]

def update_crl():
    
    # Initialize session state
    if "generated_crls" not in st.session_state:
        st.session_state.generated_crls = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Update Certificate Revocation List (CRL)")
    st.markdown("Generate and publish a new Certificate Revocation List")
    
    st.divider()
    
    # Get mock data
    revoked_certs = get_mock_revoked_certificates()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("❌ Revoked Certificates", len(revoked_certs))
    with col2:
        st.metric("📋 Last Update", "2 hours ago")
    with col3:
        st.metric("⏰ Next Update", "2 hours")
    with col4:
        st.metric("📊 CRL Version", "3")
    
    st.divider()
    
    # Create two tabs: Generate CRL & View History
    tab1, tab2 = st.tabs([" Generate New CRL", " CRL History"])
    
    with tab1:
        st.subheader("Generate New Certificate Revocation List")
        
        # Revoked Certificates Table
        st.markdown("**📄 Revoked Certificates to Include**")
        
        # Convert to DataFrame for display
        crl_data = [{
            "Certificate ID": cert.certificate_id,
            "Serial Number": cert.serial_number,
            "Subject": cert.subject_dn,
            "Revoked Date": cert.revoked_at.strftime('%Y-%m-%d %H:%M'),
            "Reason": cert.revocation_reason
        } for cert in revoked_certs]
        
        df_revoked = pd.DataFrame(crl_data)
        st.dataframe(
            df_revoked,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Certificate ID": st.column_config.NumberColumn(width="small"),
                "Serial Number": st.column_config.TextColumn(width="medium"),
                "Subject": st.column_config.TextColumn(width="large"),
                "Revoked Date": st.column_config.TextColumn(width="medium"),
                "Reason": st.column_config.TextColumn(width="medium")
            }
        )
        
        st.divider()
        
        # CRL Configuration Section
        st.markdown("**⚙️ CRL Configuration**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            validity_days = st.number_input(
                "CRL Validity Period (days):",
                min_value=1,
                max_value=365,
                value=7,
                step=1,
                key="crl_validity_days"
            )
            
            st.markdown(f"""
            **Validity Details:**
            - Issue Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            - Next Update: {(datetime.now() + timedelta(days=validity_days)).strftime('%Y-%m-%d %H:%M:%S')}
            """)
        
        with col2:
            hash_algorithm = st.selectbox(
                "Hash Algorithm:",
                options=["SHA256", "SHA384", "SHA512"],
                index=0,
                key="crl_hash_algorithm"
            )
            
            st.markdown(f"""
            **CRL Settings:**
            - Algorithm: `{hash_algorithm}`
            - Certificates Included: `{len(revoked_certs)}`
            - Format: X.509 v2
            """)
   
        # CRL Information
        with st.expander("ℹ️ CRL Information"):
            st.markdown("""
            **Certificate Revocation List (CRL):**
            - Signed by the Certificate Authority (CA)
            - Contains all revoked certificates
            - Periodically published and updated
            - Used by clients to verify certificate validity
            - Superseded by OCSP in some implementations
            
            **CRL Contents:**
            - Revoked Certificate Serial Numbers
            - Revocation Dates
            - Revocation Reasons
            - CRL Authority Signature
            """)
        
      
        # Configuration Summary
        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #f6ad55; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #f6ad55; margin-bottom: 10px;">📝 CRL Generation Summary</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> <strong>{len(revoked_certs)}</strong> revoked certificates will be included</div>
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> CRL valid for <strong>{validity_days} days</strong></div>
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> Hash algorithm: <strong>{hash_algorithm}</strong></div>
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> CRL will be signed with CA private key</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        confirm_generate = st.checkbox(
            "✓ I confirm the CRL generation parameters",
            key="confirm_crl_generate"
        )
        
        if st.button(
            "📝 Generate CRL",
            disabled=not confirm_generate,
            key="btn_generate_crl",
            use_container_width=True
        ):
            # Simulate CRL generation
            with st.spinner("Generating Certificate Revocation List..."):
                import time
                time.sleep(2)
                
                # Mock CRL PEM
                mock_crl_pem = f"""-----BEGIN X509 CRL-----
                MIIDjTCCAnWgAwIBAgIUKvN/q9X9vY6V2j7tQzZWHfRHzCowDQYJKoZIhvcNAQEL
                BQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
                GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZBcNMjYwNTIxMTAwMDAwWhcNMjYwNTI4
                MDAwMDAwWjCBgzA1BgNVHRwELjAsMiopA1UEBgECBzovMAkGA1UEBhMCQVU7MAkG
                A1UEBhMCAVU7MAkGA1UEBhMCAltVMAkGA1UEBhMCAltVMAkGA1UEBhMCAltVMAkG
                A1UEBhMCAltVMAkGA1UEBhMCAltVMAkGA1UEBhMCAltVoAoGCCsGAQQBgI4CBDAA
                DQYJKoZIhvcNAQELBQADggEBAGVFqK2yzBWqpvgS9j4kV6J5vWvqY2zRB7U/aCnI
                2M9R2I+KN7Pt4nZkJ5sC1aY9E4K8Nw7z1e0vJ5x0K+3V6Z+H1vM0Q8e+4vZ7Gj9T
                -----END X509 CRL-----
                """
                
                # Store in session
                new_crl = {
                    "id": len(st.session_state.generated_crls) + 1,
                    "generated_at": datetime.now(),
                    "validity_days": validity_days,
                    "hash_algorithm": hash_algorithm,
                    "revoked_count": len(revoked_certs),
                    "crl_pem": mock_crl_pem,
                    "version": 3
                }
                st.session_state.generated_crls.append(new_crl)
                
                st.success(f"""
                ✅ Certificate Revocation List Generated Successfully!
                
                **CRL Details:**
                - **Generated:** {new_crl['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}
                - **Valid Until:** {(new_crl['generated_at'] + timedelta(days=validity_days)).strftime('%Y-%m-%d %H:%M:%S')}
                - **Hash Algorithm:** {hash_algorithm}
                - **Revoked Certificates:** {len(revoked_certs)}
                - **CRL Version:** {new_crl['version']}
                
                **⚠️ Next Steps:**
                1. Review the CRL content below
                2. Publish CRL to LDAP/HTTP endpoints
                3. Notify subscribers of CRL update
                """)
                
                # Display CRL PEM
                st.markdown("**📄 Generated CRL (PEM Format):**")
                st.text_area(
                    "CRL Content",
                    value=mock_crl_pem,
                    height=200,
                    disabled=True,
                    key="crl_pem_display"
                )
                
                # Download options
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📥 Download CRL (PEM)", key="download_crl_pem"):
                        st.info("Download initiated - Feature would trigger actual download")
                
                with col2:
                    if st.button("📥 Download CRL (DER)", key="download_crl_der"):
                        st.info("Download initiated - Feature would trigger actual download")
                
                with col3:
                    if st.button("📤 Publish to LDAP", key="publish_crl_ldap"):
                        st.info("CRL published to LDAP server")
    
    with tab2:
        st.subheader("CRL Generation History")
        
        if not st.session_state.generated_crls:
            st.info("No CRL generation history yet.")
        else:
            # Display generated CRLs
            for crl in reversed(st.session_state.generated_crls):
                with st.expander(f"📝 CRL #{crl['id']} - Generated {crl['generated_at'].strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Generated:** {crl['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Validity:** {crl['validity_days']} days")
                        st.write(f"**Hash Algorithm:** {crl['hash_algorithm']}")
                    
                    with col2:
                        st.write(f"**Revoked Certs:** {crl['revoked_count']}")
                        st.write(f"**CRL Version:** {crl['version']}")
                        valid_until = crl['generated_at'] + timedelta(days=crl['validity_days'])
                        st.write(f"**Valid Until:** {valid_until.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    st.divider()
                    
                    st.markdown("**CRL Content (PEM):**")
                    st.markdown(f"""
                    <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
                    <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{crl['crl_pem']}</pre>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📥 Download", key=f"download_history_{crl['id']}"):
                            st.info(f"Download CRL #{crl['id']}")
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_crl_{crl['id']}"):
                            st.warning(f"CRL #{crl['id']} deletion initiated")
