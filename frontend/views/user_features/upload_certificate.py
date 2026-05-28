import streamlit as st
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
import pandas as pd

@dataclass
class UploadedCertificate:
    id: int
    filename: str
    subject: str
    issuer: str
    serial_number: str
    valid_from: datetime
    valid_to: datetime
    uploaded_at: datetime
    status: str

def get_mock_uploaded_certificates() -> List[UploadedCertificate]:
    """Generate mock uploaded certificates"""
    return [
        UploadedCertificate(
            id=1,
            filename="google.crt",
            subject="CN=*.google.com,O=Google LLC,C=US",
            issuer="CN=Google Internet Authority G3,O=Google Trust Services,C=US",
            serial_number="01:A2:B3:C4:D5:E6:F7:08",
            valid_from=datetime.now() - timedelta(days=100),
            valid_to=datetime.now() + timedelta(days=265),
            uploaded_at=datetime.now() - timedelta(days=50),
            status="VALID"
        ),
        UploadedCertificate(
            id=2,
            filename="github.crt",
            subject="CN=github.com,O=GitHub Inc,C=US",
            issuer="CN=DigiCert High Assurance TLS Hybrid,O=DigiCert Inc,C=US",
            serial_number="02:B3:C4:D5:E6:F7:08:09",
            valid_from=datetime.now() - timedelta(days=200),
            valid_to=datetime.now() + timedelta(days=165),
            uploaded_at=datetime.now() - timedelta(days=100),
            status="VALID"
        ),
        UploadedCertificate(
            id=3,
            filename="old_certificate.crt",
            subject="CN=example.old,O=Old Company,C=US",
            issuer="CN=Old CA,O=Old Company,C=US",
            serial_number="03:C4:D5:E6:F7:08:09:0A",
            valid_from=datetime.now() - timedelta(days=400),
            valid_to=datetime.now() - timedelta(days=35),
            uploaded_at=datetime.now() - timedelta(days=200),
            status="EXPIRED"
        ),
    ]

def upload_certificate():
    
    # Initialize session state
    if "uploaded_certs" not in st.session_state:
        st.session_state.uploaded_certs = []
    
    # Back button
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title("📤 Upload & Monitor Certificates")
    st.markdown("Upload certificates from other sources to track and monitor them")
    
    st.divider()
    
    # Create tabs
    tab1, tab2 = st.tabs(["📤 Upload Certificate", "📋 Uploaded Certificates"])
    
    with tab1:
        st.subheader("Upload a Certificate File")
        
        # Upload method
        upload_method = st.radio(
            "How would you like to upload?",
            ["File Upload", "Paste PEM Content"],
            key="upload_method"
        )
        
        st.divider()
        
        if upload_method == "File Upload":
            # File upload
            uploaded_file = st.file_uploader(
                "Choose a certificate file (CRT, PEM, DER, CERT):",
                type=["crt", "pem", "der", "cert", "cer"],
                key="cert_file"
            )
            
            if uploaded_file:
                st.success(f"✅ File selected: {uploaded_file.name}")
        
        else:
            # Paste PEM
            cert_pem = st.text_area(
                "Paste certificate in PEM format:",
                placeholder="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
                height=200,
                key="cert_pem_paste"
            )
        
        st.divider()
        
        # Certificate details
        st.markdown("**📝 Certificate Details (Optional):**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cert_name = st.text_input(
                "Certificate Name/Description:",
                placeholder="e.g., Google SSL, GitHub HTTPS, etc.",
                key="cert_name"
            )
            
            domain = st.text_input(
                "Associated Domain (optional):",
                placeholder="example.com",
                key="cert_domain"
            )
        
        with col2:
            notes = st.text_area(
                "Notes/Comments (optional):",
                placeholder="Add any additional notes about this certificate...",
                height=100,
                key="cert_notes"
            )
        
        st.divider()
        
        if st.button(
            "📤 Upload Certificate",
            use_container_width=True,
            key="btn_upload_cert"
        ):
            has_content = (uploaded_file if upload_method == "File Upload" else cert_pem) and cert_name
            
            if not has_content:
                st.error("❌ Please provide a certificate file/content and a name")
            else:
                new_upload = {
                    "id": len(st.session_state.uploaded_certs) + 1,
                    "name": cert_name,
                    "domain": domain,
                    "filename": uploaded_file.name if upload_method == "File Upload" else "pasted_cert.pem",
                    "timestamp": datetime.now(),
                }
                st.session_state.uploaded_certs.append(new_upload)
                
                st.success(f"""
                ✅ Certificate Uploaded Successfully!
                
                **Upload Details:**
                - **Name:** {cert_name}
                - **Domain:** {domain if domain else 'Not specified'}
                - **Uploaded:** {new_upload['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                - **Monitoring Active:** {'Yes' if new_upload['monitoring'] else 'No'}
                
                Your certificate is now being monitored and tracked in the system.
                """)
    
    with tab2:
        st.subheader("Uploaded Certificates")
        
        uploaded_certs = get_mock_uploaded_certificates()
        
        if not uploaded_certs:
            st.info("No uploaded certificates yet. Start by uploading a certificate.")
        else:
            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📋 Total Uploaded", len(uploaded_certs))
            with col2:
                st.metric("✅ Valid", len([c for c in uploaded_certs if c.status == "VALID"]))
            with col3:
                st.metric("⏰ Expired", len([c for c in uploaded_certs if c.status == "EXPIRED"]))
            
            st.divider()
            
            # Display as table
            cert_data = []
            for cert in uploaded_certs:
                days_left = (cert.valid_to - datetime.now()).days
                if cert.status == "VALID":
                    validity = f"{days_left}d left"
                else:
                    validity = "Expired"
                
                cert_data.append({
                    "Filename": cert.filename,
                    "Subject (CN)": cert.subject.split(",")[0].replace("CN=", ""),
                    "Valid To": cert.valid_to.strftime('%Y-%m-%d'),
                    "Status": cert.status,
                    "Validity": validity,
                    "Uploaded": cert.uploaded_at.strftime('%Y-%m-%d')
                })
            
            df = pd.DataFrame(cert_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Filename": st.column_config.TextColumn(width="medium"),
                    "Subject (CN)": st.column_config.TextColumn(width="large"),
                    "Valid To": st.column_config.TextColumn(width="medium"),
                    "Status": st.column_config.TextColumn(width="small"),
                    "Validity": st.column_config.TextColumn(width="medium"),
                    "Uploaded": st.column_config.TextColumn(width="medium")
                }
            )
            
            st.divider()
            
            # Detailed view
            st.markdown("**📄 Detailed Information**")
            
            selected_idx = st.selectbox(
                "Select a certificate for details:",
                range(len(uploaded_certs)),
                format_func=lambda i: uploaded_certs[i].filename,
                key="upload_detail_select"
            )
            
            selected_cert = uploaded_certs[selected_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Filename:** {selected_cert.filename}")
                st.write(f"**Subject:** `{selected_cert.subject}`")
                st.write(f"**Issuer:** `{selected_cert.issuer}`")
                st.write(f"**Serial Number:** `{selected_cert.serial_number}`")
            
            with col2:
                st.write(f"**Valid From:** {selected_cert.valid_from.strftime('%Y-%m-%d')}")
                st.write(f"**Valid To:** {selected_cert.valid_to.strftime('%Y-%m-%d')}")
                st.write(f"**Status:** {selected_cert.status}")
                st.write(f"**Uploaded:** {selected_cert.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            st.divider()

