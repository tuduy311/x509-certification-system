import streamlit as st
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List

# Enums
class CertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class HashAlgorithm(str, Enum):
    SHA256 = "SHA256"
    SHA384 = "SHA384"
    SHA512 = "SHA512"

# Mock Data Model
@dataclass
class RootCertificateOut:
    id: int
    serial_number: str
    subject_dn: str
    issuer_dn: str
    valid_from: datetime
    valid_to: datetime
    hash_algorithm: HashAlgorithm
    status: CertStatus
    cert_pem: str
    created_at: datetime

# Mock Data Generator
def get_mock_root_certificates() -> List[RootCertificateOut]:
    """Generate mock root certificate records"""
    return [
        RootCertificateOut(
            id=1,
            serial_number="01:A2:B3:C4:D5:E6:F7:08:09:0A",
            subject_dn="CN=CA Root Certificate,O=Organization,C=US",
            issuer_dn="CN=CA Root Certificate,O=Organization,C=US",
            valid_from=datetime(2026, 1, 15),
            valid_to=datetime(2035, 1, 15),
            hash_algorithm=HashAlgorithm.SHA256,
            status=CertStatus.ACTIVE,
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDazCCAlOgAwIBAgIUJArAoMg9N8DhFblVGQJK/tgK7nswDQYJKoZIhvcNAQEL\nBQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM\nGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yNjAxMTUxMDMwMDBaFw0zNTAx\nMTUxMDMwMDBaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw\nHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggEiMA0GCSqGSIb3DQEB\nAQUAA4IBDwAwggEKAoIBAQC7VJTUt9Us8cKjMzEfYyjiWA4/4ggCnQvj-----END CERTIFICATE-----",
            created_at=datetime(2026, 1, 15, 10, 30)
        ),
        RootCertificateOut(
            id=2,
            serial_number="02:B3:C4:D5:E6:F7:08:09:0A:0B",
            subject_dn="CN=CA Root Test,O=Organization,C=US",
            issuer_dn="CN=CA Root Test,O=Organization,C=US",
            valid_from=datetime(2025, 12, 1),
            valid_to=datetime(2026, 12, 1),
            hash_algorithm=HashAlgorithm.SHA384,
            status=CertStatus.EXPIRED,
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDazCCAlOgAwIBAgIUJArAoMg9N8DhFblVGQJK/tgK7nswDQYJKoZIhvcNAQEL\nBQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM\nGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yNjAxMTUxMDMwMDBaFw0zNTAx\nMTUxMDMwMDBaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw\nHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggEiMA0GCSqGSIb3DQEB\nAQUAA4IBDwAwggEKAoIBAQC7VJTUt9Us8cKjMzEfYyjiWA4/4ggCnQvj-----END CERTIFICATE-----",
            created_at=datetime(2025, 12, 1, 14, 15)
        ),
        RootCertificateOut(
            id=3,
            serial_number="03:C4:D5:E6:F7:08:09:0A:0B:0C",
            subject_dn="CN=CA Root Revoked,O=Organization,C=US",
            issuer_dn="CN=CA Root Revoked,O=Organization,C=US",
            valid_from=datetime(2025, 11, 1),
            valid_to=datetime(2026, 11, 1),
            hash_algorithm=HashAlgorithm.SHA512,
            status=CertStatus.REVOKED,
            cert_pem="-----BEGIN CERTIFICATE-----\nMIIDazCCAlOgAwIBAgIUJArAoMg9N8DhFblVGQJK/tgK7nswDQYJKoZIhvcNAQEL\nBQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM\nGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yNjAxMTUxMDMwMDBaFw0zNTAx\nMTUxMDMwMDBaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw\nHwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggEiMA0GCSqGSIb3DQEB\nAQUAA4IBDwAwggEKAoIBAQC7VJTUt9Us8cKjMzEfYyjiWA4/4ggCnQvj-----END CERTIFICATE-----",
            created_at=datetime(2025, 11, 1, 9, 0)
        ),
    ]

def generate_root_certificate():
    
    # Initialize session state
    if "generated_root_certs" not in st.session_state:
        st.session_state.generated_root_certs = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Generate Root Certificate")
    st.markdown("Create a new Root Certificate Authority (CA) certificate")
    
    st.divider()
    
    # Get mock data
    all_certificates = get_mock_root_certificates()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Active", len([c for c in all_certificates if c.status == CertStatus.ACTIVE]))
    with col2:
        st.metric("📦 Total", len(all_certificates))
    with col3:
        st.metric("⏰ Expired", len([c for c in all_certificates if c.status == CertStatus.EXPIRED]))
    with col4:
        st.metric("❌ Revoked", len([c for c in all_certificates if c.status == CertStatus.REVOKED]))
    
    st.divider()
    
    # Create two tabs: Generate New & View Existing
    tab1, tab2 = st.tabs([" Generate New", " View Existing"])
    
    with tab1:
        st.subheader("Generate New Root CA Certificate")
        st.markdown("Configure parameters for the new root CA certificate")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Subject DN Components
            st.markdown("**Subject Distinguished Name (DN)**")
            
            common_name = st.text_input(
                "Common Name (CN):",
                value="My Root CA",
                key="root_cert_cn"
            )
            
            organization = st.text_input(
                "Organization (O):",
                value="My Organization",
                key="root_cert_org"
            )
            
            country = st.text_input(
                "Country Code (C):",
                value="US",
                max_chars=2,
                key="root_cert_country"
            )
            
            state = st.text_input(
                "State/Province (ST):",
                value="California",
                key="root_cert_state"
            )
        
        with col2:
            # Certificate Parameters
            st.markdown("**Certificate Parameters**")
            
            key_size = st.selectbox(
                "Key Size (bits):",
                options=[2048, 3072, 4096],
                index=0,
                key="root_cert_key_size"
            )
            
            validity_days = st.number_input(
                "Validity Period (days):",
                min_value=365,
                max_value=36500,
                value=3650,
                step=365,
                key="root_cert_validity"
            )
            
            hash_algorithm = st.selectbox(
                "Hash Algorithm:",
                options=["SHA256", "SHA384", "SHA512"],
                index=0,
                key="root_cert_hash_alg"
            )
            
            serial_number = st.text_input(
                "Serial Number (hex, auto-generated if empty):",
                value="",
                key="root_cert_serial"
            )
        
        st.divider()
        
        # Certificate Extensions
        st.markdown("**Certificate Extensions**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            add_basic_constraints = st.checkbox(
                "Basic Constraints (pathLenConstraint: -1)",
                value=True,
                key="root_cert_basic_constraints"
            )
        
        with col2:
            add_key_usage = st.checkbox(
                "Key Usage",
                value=True,
                key="root_cert_key_usage"
            )
        
        with col3:
            add_extended_key_usage = st.checkbox(
                "Extended Key Usage",
                value=True,
                key="root_cert_extended_key_usage"
            )
        
        st.divider()
        
        # X.509 Version and Profile
        col1, col2 = st.columns(2)
        
        with col1:
            x509_version = st.radio(
                "X.509 Version:",
                options=["v3"],
                key="root_cert_x509_version"
            )
        
        with col2:
            profile = st.selectbox(
                "Certificate Profile:",
                options=["Root CA", "Custom"],
                key="root_cert_profile"
            )
        
        
        
        # Confirmation and Generate
        st.markdown("""
        <div style="background-color: #2d3748; border-left: 4px solid #48bb78; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #48bb78; margin-bottom: 10px;">✓ Certificate Configuration</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> Self-signed Root CA certificate will be created</div>
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> Certificate will be valid for <strong>{validity_days} days</strong></div>
        <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">✅</span> Private key will be securely generated</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        confirm_generate = st.checkbox(
            "I understand the importance of securing the private key",
            key="confirm_root_cert_generate"
        )
        
        if st.button(
            "📜 Generate Certificate",
            disabled=not confirm_generate,
            key="btn_generate_root_cert",
            use_container_width=True
        ):
            # Simulate generation
            with st.spinner("Generating root CA certificate..."):
                import time
                time.sleep(3)
                
                # Store in session
                new_cert = {
                    "id": len(st.session_state.generated_root_certs) + 1,
                    "cn": common_name,
                    "org": organization,
                    "key_size": key_size,
                    "validity_days": validity_days,
                    "hash_alg": hash_algorithm,
                    "timestamp": datetime.now()
                }
                st.session_state.generated_root_certs.append(new_cert)
                
                st.success(f"""
                ✅ Root CA Certificate Generated Successfully!
                
                **Certificate Details:**
                - **Common Name:** {common_name}
                - **Organization:** {organization}
                - **Key Size:** {key_size} bits
                - **Hash Algorithm:** {hash_algorithm}
                - **Validity:** {validity_days} days
                - **Generated:** {new_cert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                
                **⚠️ Important:**
                1. Download the certificate and private key immediately
                2. Store private key in secure location
                3. Back up certificate in multiple locations
                4. Keep certificate secure and confidential
                """)
        
        # Security & Compliance (moved to end)
        st.divider()
        with st.expander("🛡️ Security & Compliance"):
            st.markdown("""
            **Security Best Practices:**
            - Root CA certificate should be highly protected
            - Store private key in HSM (Hardware Security Module)
            - Use strong key size (minimum 2048 bits, recommended 4096)
            - Set appropriate validity period (10 years recommended)
            - Enable all critical extensions
            
            **Compliance Standards:**
            - RFC 5280 - Internet X.509 Public Key Infrastructure
            - RFC 3739 - Internet X.509 Public Key Infrastructure
            - CA/Browser Forum Baseline Requirements
            """)
        
        # Certificate Preview (moved to end)
        with st.expander("👁️ Preview Certificate Parameters"):
            preview_dn = f"CN={common_name},O={organization},ST={state},C={country}"
            st.markdown(f"""
            **Subject DN:** `{preview_dn}`
            
            **Configuration:**
            - Key Size: `{key_size} bits`
            - Validity: `{validity_days} days` (≈ {validity_days/365:.1f} years)
            - Hash Algorithm: `{hash_algorithm}`
            - Version: `X.509 {x509_version}`
            """)
    
    with tab2:
        st.subheader("Existing Root CA Certificates")
        
        if not all_certificates:
            st.info("No root CA certificates found.")
        else:
            # Display as expandable sections
            for cert in all_certificates:
                status_color = "🟢" if cert.status == CertStatus.ACTIVE else ("🟠" if cert.status == CertStatus.EXPIRED else "🔴")
                with st.expander(f"{status_color} {cert.subject_dn} - {cert.status.value}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Certificate ID:** {cert.id}")
                        st.write(f"**Subject DN:** `{cert.subject_dn}`")
                        st.write(f"**Serial Number:** `{cert.serial_number}`")
                        st.write(f"**Status:** {cert.status.value}")
                    
                    with col2:
                        st.write(f"**Valid From:** {cert.valid_from.strftime('%Y-%m-%d')}")
                        st.write(f"**Valid To:** {cert.valid_to.strftime('%Y-%m-%d')}")
                        st.write(f"**Hash Algorithm:** {cert.hash_algorithm.value}")
                        st.write(f"**Created:** {cert.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Validity Status
                    now = datetime.now()
                    if now < cert.valid_from:
                        validity_text = "⏳ Not yet valid"
                    elif now > cert.valid_to:
                        validity_text = "❌ Expired"
                    else:
                        days_remaining = (cert.valid_to - now).days
                        validity_text = f"✅ Valid for {days_remaining} more days"
                    
                    st.markdown(f"**Validity Status:** {validity_text}")
                    
                    # Certificate PEM
                    st.markdown("**📄 Certificate (PEM):**")
                    st.markdown(f"""
                    <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
                    <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{cert.cert_pem}</pre>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Actions
                    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                    
                    with action_col1:
                        if st.button(
                            "📥 Download",
                            key=f"download_cert_{cert.id}"
                        ):
                            st.info(f"Download certificate {cert.id} - Feature would trigger actual download")
                    
                    with action_col2:
                        if st.button(
                            "📋 Copy PEM",
                            key=f"copy_pem_{cert.id}"
                        ):
                            st.success("Certificate PEM copied to clipboard!")
                    
                    with action_col3:
                        if st.button(
                            "🔍 Verify",
                            key=f"verify_cert_{cert.id}"
                        ):
                            st.info(f"Verification of certificate {cert.id} completed")
                    
                    with action_col4:
                        if cert.status == CertStatus.ACTIVE and st.button(
                            "❌ Revoke",
                            key=f"revoke_cert_{cert.id}"
                        ):
                            st.warning(f"Certificate {cert.id} revocation initiated")
            
            st.divider()
            st.markdown("**Status Legend:** 🟢 Active | 🟠 Expired | 🔴 Revoked")
        
        # Security & Compliance (moved to end)
        st.divider()
        with st.expander("🛡️ Security & Compliance"):
            st.markdown("""
            **Security Best Practices:**
            - Root CA certificate should be highly protected
            - Store private key in HSM (Hardware Security Module)
            - Use strong key size (minimum 2048 bits, recommended 4096)
            - Set appropriate validity period (10 years recommended)
            - Enable all critical extensions
            
            **Compliance Standards:**
            - RFC 5280 - Internet X.509 Public Key Infrastructure
            - RFC 3739 - Internet X.509 Public Key Infrastructure
            - CA/Browser Forum Baseline Requirements
            """)
        
        # Certificate Preview (moved to end)
        with st.expander("👁️ Preview Certificate Parameters"):
            preview_dn = f"CN={common_name},O={organization},ST={state},C={country}"
            st.markdown(f"""
            **Subject DN:** `{preview_dn}`
            
            **Configuration:**
            - Key Size: `{key_size} bits`
            - Validity: `{validity_days} days` (≈ {validity_days/365:.1f} years)
            - Hash Algorithm: `{hash_algorithm}`
            - Version: `X.509 {x509_version}`
            """)
