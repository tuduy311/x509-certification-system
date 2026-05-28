import streamlit as st
from datetime import datetime
import pandas as pd
import requests as http_requests
import api.api_client as api_client


def upload_certificate():

    # ── Back button ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    # ── Header ──
    st.title("📤 Upload & Monitor Certificates")
    st.markdown("Upload certificates from other sources to track and monitor them")

    st.divider()

    # ── Create tabs ──
    tab1, tab2 = st.tabs(["📤 Upload Certificate", "📋 Uploaded Certificates"])

    # ═══════════════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("Upload a Certificate File")

        # Upload method
        upload_method = st.radio(
            "How would you like to upload?",
            ["File Upload", "Paste PEM Content"],
            key="upload_method"
        )

        st.divider()

        cert_pem_content = ""
        filename = ""

        if upload_method == "File Upload":
            # File upload
            uploaded_file = st.file_uploader(
                "Choose a certificate file (CRT, PEM, DER, CERT):",
                type=["crt", "pem", "der", "cert", "cer"],
                key="cert_file"
            )

            if uploaded_file:
                st.success(f"✅ File selected: {uploaded_file.name}")
                try:
                    cert_pem_content = uploaded_file.getvalue().decode("utf-8")
                    filename = uploaded_file.name
                except Exception as e:
                    st.error(f"❌ Failed to read file content: {e}")
        else:
            # Paste PEM
            cert_pem = st.text_area(
                "Paste certificate in PEM format:",
                placeholder="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
                height=200,
                key="cert_pem_paste"
            )
            
            pasted_filename = st.text_input(
                "Filename for pasted content:",
                placeholder="Ex: example.pem",
                key="pasted_filename_input"
            )
            
            if cert_pem.strip():
                cert_pem_content = cert_pem.strip()
                filename = pasted_filename.strip() if pasted_filename.strip() else "pasted_cert.pem"

        st.divider()

        if st.button(
            "📤 Upload Certificate",
            use_container_width=True,
            key="btn_upload_cert"
        ):
            if not cert_pem_content:
                st.error("❌ Please provide a certificate file or paste PEM content first.")
            else:
                with st.spinner("Uploading and parsing certificate on server..."):
                    try:
                        # Upload to backend database
                        result = api_client.upload_monitored_certificate(filename, cert_pem_content)
                        
                        st.success(f"""
                        ✅ **Certificate Uploaded Successfully!**
                        
                        **Upload Details:**
                        - **ID:** {result.get('id')}
                        - **Filename:** {result.get('filename')}
                        - **Subject CN:** {result.get('subject', '').split('CN=')[-1].split(',')[0]}
                        - **Serial:** {result.get('serial_number')}
                        - **Valid To:** {str(result.get('valid_to'))[:19]}
                        - **Status:** {result.get('status')}
                        """)
                        
                        # Clear inputs in session state (safely skipped to prevent Streamlit widget mutation errors)
                        pass
                            
                            
                    except http_requests.HTTPError as e:
                        if e.response is not None:
                            detail = e.response.json().get("detail", str(e))
                            st.error(f"❌ Upload failed: {detail}")
                        else:
                            st.error(f"❌ Upload failed: {e}")
                    except http_requests.ConnectionError:
                        st.error("❌ Cannot connect to backend server.")

    # ═══════════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("Uploaded Certificates")

        # Fetch live data from backend APIs
        uploaded_certs = []
        try:
            uploaded_certs = api_client.get_monitored_certificates()
        except http_requests.ConnectionError:
            st.error("❌ Cannot connect to backend server to load certificates.")
        except Exception as e:
            st.error(f"❌ Error loading certificates: {e}")

        if not uploaded_certs:
            st.info("No uploaded certificates yet. Start by uploading a certificate.")
        else:
            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📋 Total Uploaded", len(uploaded_certs))
            with col2:
                st.metric("✅ Valid", len([c for c in uploaded_certs if c.get("status") == "VALID"]))
            with col3:
                st.metric("⏰ Expired", len([c for c in uploaded_certs if c.get("status") == "EXPIRED"]))

            st.divider()

            # Display as table
            cert_data = []
            for cert in uploaded_certs:
                # Calculate days left dynamically from returned valid_to string/datetime
                valid_to_str = cert.get("valid_to", "")
                days_left = 0
                try:
                    # Backend returns ISO datetime format like "2026-05-28T16:21:09"
                    valid_to_dt = datetime.fromisoformat(valid_to_str.replace("Z", ""))
                    days_left = (valid_to_dt - datetime.now()).days
                except Exception:
                    pass

                status = cert.get("status", "VALID")
                if status == "VALID":
                    validity = f"{days_left}d left"
                else:
                    validity = "Expired"

                # Parse Common Name from subject flat string
                subject_str = cert.get("subject", "")
                cn_val = "Unknown"
                for part in subject_str.split(","):
                    if part.startswith("CN="):
                        cn_val = part.split("=")[-1]
                        break

                # Parse Upload date
                created_at_str = cert.get("created_at", "")
                try:
                    created_dt = datetime.fromisoformat(created_at_str.replace("Z", ""))
                    uploaded_date = created_dt.strftime('%Y-%m-%d')
                except Exception:
                    uploaded_date = str(created_at_str)[:10]

                cert_data.append({
                    "Filename": cert.get("filename", "Unknown"),
                    "Subject (CN)": cn_val,
                    "Valid To": str(valid_to_str)[:10],
                    "Status": status,
                    "Validity": validity,
                    "Uploaded": uploaded_date
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
                format_func=lambda i: uploaded_certs[i].get("filename", "Unknown"),
                key="upload_detail_select"
            )

            selected_cert = uploaded_certs[selected_idx]

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Filename:** {selected_cert.get('filename')}")
                st.write(f"**Subject:** `{selected_cert.get('subject')}`")
                st.write(f"**Issuer:** `{selected_cert.get('issuer')}`")
                st.write(f"**Serial Number:** `{selected_cert.get('serial_number')}`")

            with col2:
                # format validity dates
                vf = selected_cert.get("valid_from", "")
                vt = selected_cert.get("valid_to", "")
                
                st.write(f"**Valid From:** {str(vf)[:19].replace('T', ' ')}")
                st.write(f"**Valid To:** {str(vt)[:19].replace('T', ' ')}")
                st.write(f"**Status:** {selected_cert.get('status')}")
                
                created_str = selected_cert.get("created_at", "")
                st.write(f"**Uploaded:** {str(created_str)[:19].replace('T', ' ')}")

            st.divider()
