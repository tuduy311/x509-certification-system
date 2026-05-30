import streamlit as st
from datetime import datetime
import pandas as pd
import api.api_client as api_client
import requests as http_requests
from views._cert_display import render_certificate


def my_certificates():

    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()
    st.title("📋 My Certificates")
    st.markdown("View and manage your X.509 certificates issued by this CA.")
    st.divider()

    # ── Fetch certificate list ────────────────────────────────────────────────
    try:
        all_certs = api_client.get_my_certificates()
    except http_requests.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return
    except http_requests.HTTPError as e:
        st.error(f"Backend error: {e}")
        return

    # ── Statistics ────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Active",  len([c for c in all_certs if c["status"] == "approved"]))
    with col2:
        st.metric("⏰ Expired", len([c for c in all_certs if c["status"] == "expired"]))
    with col3:
        st.metric("❌ Revoked", len([c for c in all_certs if c["status"] == "revoked"]))
    with col4:
        st.metric("📊 Total",   len(all_certs))

    st.divider()

    tab1, tab2 = st.tabs(["📋 All Certificates", "🔍 Certificate Details"])

    # ═══════════════ TAB 1 — summary table ═══════════════════════════════════
    with tab1:
        if not all_certs:
            st.info("You don't have any certificates yet. Submit a Certificate Signing Request to get started.")
        else:
            now = datetime.utcnow()
            cert_data = []
            for cert in all_certs:
                try:
                    valid_to = datetime.fromisoformat(
                        str(cert["valid_to"]).replace("T", " ").split(".")[0]
                    )
                    if cert["status"] == "approved":
                        days_left = (valid_to - now).days
                        validity = f"✅ {days_left}d left"
                    elif cert["status"] == "revoked":
                        validity = "❌ Revoked"
                    else:
                        validity = "⏰ Expired"
                except Exception:
                    validity = cert["status"].upper()

                serial = cert["serial_number"]
                try:
                    serial_hex = hex(int(serial)).upper().replace("0X", "")
                except Exception:
                    serial_hex = serial

                cert_data.append({
                    "ID":           cert["id"],
                    "Serial (hex)": serial_hex,
                    "Status":       cert["status"].upper(),
                    "Valid From":   str(cert["valid_from"])[:10],
                    "Valid To":     str(cert["valid_to"])[:10],
                    "Validity":     validity,
                })

            df = pd.DataFrame(cert_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID":           st.column_config.NumberColumn(width="small"),
                    "Serial (hex)": st.column_config.TextColumn(width="large"),
                    "Status":       st.column_config.TextColumn(width="medium"),
                    "Valid From":   st.column_config.TextColumn(width="medium"),
                    "Valid To":     st.column_config.TextColumn(width="medium"),
                    "Validity":     st.column_config.TextColumn(width="medium"),
                }
            )

    # ═══════════════ TAB 2 — certificate viewer ═══════════════════════════════
    with tab2:
        if not all_certs:
            st.info("No certificates to display.")
        else:
            cert_options = [
                f"#{c['id']}  {c['status'].upper()}  —  "
                + ("Expires: " + str(c["valid_to"])[:10] if c["status"] == "approved"
                   else str(c["valid_to"])[:10])
                for c in all_certs
            ]
            selected_idx = st.selectbox(
                "Select a certificate to view:",
                range(len(all_certs)),
                format_func=lambda i: cert_options[i],
                key="cert_detail_select"
            )

            selected_cert = all_certs[selected_idx]

            st.divider()

            # ── Fetch parsed info from backend ────────────────────────────────
            info_key = f"cert_info_{selected_cert['id']}"
            if info_key not in st.session_state:
                with st.spinner("Parsing certificate..."):
                    try:
                        st.session_state[info_key] = api_client.get_certificate_info(
                            selected_cert["id"]
                        )
                    except http_requests.HTTPError as e:
                        st.error(f"❌ Could not parse certificate: {e}")
                        st.session_state[info_key] = None
                    except http_requests.ConnectionError:
                        st.error("❌ Cannot connect to backend.")
                        st.session_state[info_key] = None

            info = st.session_state.get(info_key)
            if info:
                render_certificate(info, selected_cert)
            else:
                st.warning("Certificate information could not be loaded.")

            st.divider()

            # ── Actions ───────────────────────────────────────────────────────
            col1, col2 = st.columns(2)
            with col1:
                # Download PEM — fetch from the list already loaded
                pem = selected_cert.get("cert_pem", "")
                if pem:
                    st.download_button(
                        label="📥 Download Certificate (PEM)",
                        data=pem,
                        file_name=f"cert_{selected_cert['id']}.pem",
                        mime="application/x-pem-file",
                        key=f"dl_cert_{selected_cert['id']}",
                        use_container_width=True,
                    )
