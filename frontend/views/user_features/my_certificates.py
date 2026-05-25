import streamlit as st
from datetime import datetime
import pandas as pd
import api_client
import requests as http_requests


def my_certificates():

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("📋 My Certificates")
    st.markdown("View and manage your X.509 certificates")
    st.divider()

    # ── Fetch from backend ──
    try:
        all_certs = api_client.get_my_certificates()
    except http_requests.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return
    except http_requests.HTTPError as e:
        st.error(f"Backend error: {e}")
        return

    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Active", len([c for c in all_certs if c["status"] == "approved"]))
    with col2:
        st.metric("⏰ Expired", len([c for c in all_certs if c["status"] == "expired"]))
    with col3:
        st.metric("📊 Total", len(all_certs))

    st.divider()

    tab1, tab2 = st.tabs(["📋 All Certificates", "🔍 Details"])

    with tab1:
        st.subheader("My Certificates")

        if not all_certs:
            st.info("You don't have any certificates yet. Submit a Certificate Signing Request to get started.")
        else:
            now = datetime.utcnow()
            cert_data = []
            for cert in all_certs:
                try:
                    valid_to = datetime.fromisoformat(str(cert["valid_to"]).replace("T", " ").split(".")[0])
                    if cert["status"] == "approved":
                        days_left = (valid_to - now).days
                        validity = f"✅ {days_left}d left"
                    elif cert["status"] == "revoked":
                        validity = "❌ Revoked"
                    else:
                        validity = "⏰ Expired"
                except Exception:
                    validity = cert["status"].upper()

                cert_data.append({
                    "ID": cert["id"],
                    "Serial Number": cert["serial_number"],
                    "Status": cert["status"].upper(),
                    "Valid From": str(cert["valid_from"])[:10],
                    "Valid To": str(cert["valid_to"])[:10],
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

        if not all_certs:
            st.info("No certificates to display.")
        else:
            cert_options = [f"Cert #{c['id']} - {c['status'].upper()}" for c in all_certs]
            selected_idx = st.selectbox(
                "Select a certificate to view details:",
                range(len(all_certs)),
                format_func=lambda i: cert_options[i],
                key="cert_detail_select"
            )

            selected_cert = all_certs[selected_idx]

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Certificate ID:** {selected_cert['id']}")
                st.write(f"**Serial Number:** `{selected_cert['serial_number']}`")
                st.write(f"**Status:** {selected_cert['status'].upper()}")

            with col2:
                st.write(f"**Created:** {str(selected_cert['created_at'])[:19]}")
                st.write(f"**Valid From:** {str(selected_cert['valid_from'])[:10]}")
                st.write(f"**Valid To:** {str(selected_cert['valid_to'])[:10]}")

                if selected_cert["status"] == "approved":
                    try:
                        valid_to = datetime.fromisoformat(str(selected_cert["valid_to"]).replace("T", " ").split(".")[0])
                        days_left = (valid_to - datetime.utcnow()).days
                        st.write(f"**Days Until Expiry:** {days_left} days")
                    except Exception:
                        pass

            st.divider()

            st.markdown("**📄 Certificate (PEM):**")
            st.markdown(f"""
            <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
            <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{selected_cert['cert_pem']}</pre>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.download_button(
                    label="📥 Download Certificate",
                    data=selected_cert["cert_pem"],
                    file_name=f"cert_{selected_cert['id']}.pem",
                    mime="application/x-pem-file",
                    key=f"download_cert_{selected_cert['id']}"
                )

            with col2:
                if st.button("🔍 Parse Certificate", key=f"parse_cert_{selected_cert['id']}"):
                    try:
                        info = api_client.parse_certificate(selected_cert["cert_pem"])
                        st.json(info)
                    except Exception as e:
                        st.error(f"Parse error: {e}")

            with col3:
                if selected_cert["status"] == "approved":
                    if st.button("🔄 Renew", key=f"renew_cert_{selected_cert['id']}"):
                        st.session_state.current_feature = "renew_certificate"
                        st.rerun()
