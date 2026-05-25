import streamlit as st
import pandas as pd
import api_client
import requests as http_requests

def issued_certificates():

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("📋 Issued Certificates")
    st.markdown("View and manage all issued X.509 certificates")
    st.divider()

    # ── Fetch data from backend ──
    try:
        all_certificates = api_client.get_all_certificates()
        revocation_requests = api_client.get_revocation_requests()
    except http_requests.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return
    except http_requests.HTTPError as e:
        st.error(f"Backend error: {e}")
        return

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Active", len([c for c in all_certificates if c["status"] == "approved"]))
    with col2:
        st.metric("❌ Revoked", len([c for c in all_certificates if c["status"] == "revoked"]))
    with col3:
        st.metric("⏰ Expired", len([c for c in all_certificates if c["status"] == "expired"]))
    with col4:
        st.metric("📊 Total", len(all_certificates))

    st.divider()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 All Certificates", "🔍 Details", "🔄 Revocation Requests"])

    # ── TAB 1: All Certificates ──
    with tab1:
        st.subheader("Issued Certificates List")

        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect(
                "Filter by Status:",
                options=["approved", "revoked", "expired", "pending"],
                default=["approved", "revoked", "expired"],
                key="cert_status_filter"
            )
        with col2:
            search_user = st.text_input("Search by User ID:", key="cert_search_user")
        with col3:
            search_serial = st.text_input("Search by Serial Number:", key="cert_search_serial")

        filtered_certs = all_certificates
        if status_filter:
            filtered_certs = [c for c in filtered_certs if c["status"] in status_filter]
        if search_user:
            filtered_certs = [c for c in filtered_certs if str(c["user_id"]) == search_user]
        if search_serial:
            filtered_certs = [c for c in filtered_certs if search_serial.lower() in c["serial_number"].lower()]

        cert_data = []
        for cert in filtered_certs:
            valid_to = str(cert["valid_to"])[:10]
            valid_from = str(cert["valid_from"])[:10]
            status = cert["status"].upper()
            cert_data.append({
                "ID": cert["id"],
                "Serial Number": cert["serial_number"],
                "User ID": cert["user_id"],
                "Status": status,
                "Valid From": valid_from,
                "Valid To": valid_to,
            })

        df = pd.DataFrame(cert_data) if cert_data else pd.DataFrame()
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.info(f"📊 Showing {len(cert_data)} of {len(all_certificates)} certificates")

    # ── TAB 2: Details ──
    with tab2:
        st.subheader("Certificate Details")

        if not all_certificates:
            st.info("No certificates issued yet.")
        else:
            cert_options = [f"Cert #{c['id']} - User {c['user_id']} - {c['status'].upper()}" for c in all_certificates]
            selected_idx = st.selectbox(
                "Select a certificate to view details:",
                range(len(all_certificates)),
                format_func=lambda i: cert_options[i],
                key="cert_detail_select"
            )

            selected_cert = all_certificates[selected_idx]

            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Certificate ID:** {selected_cert['id']}")
                st.write(f"**Serial Number:** `{selected_cert['serial_number']}`")
                st.write(f"**User ID:** {selected_cert['user_id']}")
                st.write(f"**Request ID:** {selected_cert.get('request_id', 'N/A')}")
                st.write(f"**Status:** {selected_cert['status'].upper()}")

            with col2:
                st.write(f"**Created:** {str(selected_cert['created_at'])[:19]}")
                st.write(f"**Valid From:** {str(selected_cert['valid_from'])[:10]}")
                st.write(f"**Valid To:** {str(selected_cert['valid_to'])[:10]}")

            st.divider()
            st.markdown("**📄 Certificate (PEM):**")
            st.markdown(f"""
            <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
            <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{selected_cert['cert_pem']}</pre>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Certificate",
                    data=selected_cert["cert_pem"],
                    file_name=f"cert_{selected_cert['id']}.pem",
                    mime="application/x-pem-file"
                )
            with col2:
                if selected_cert["status"] == "approved":
                    if st.button("❌ Revoke", key=f"quick_revoke_{selected_cert['id']}"):
                        try:
                            api_client.admin_revoke_certificate(selected_cert["id"])
                            st.warning(f"Certificate #{selected_cert['id']} has been revoked.")
                            st.rerun()
                        except http_requests.HTTPError as e:
                            detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                            st.error(f"Error: {detail}")

    # ── TAB 3: Revocation Requests ──
    with tab3:
        st.subheader("Revocation Requests")

        pending_revokes = [r for r in revocation_requests if r["status"] == "pending"]

        if not revocation_requests:
            st.info("No revocation requests found.")
        else:
            revoke_data = []
            for rv in revocation_requests:
                revoke_data.append({
                    "Request ID": rv["id"],
                    "Certificate ID": rv["certificate_id"],
                    "User ID": rv["user_id"],
                    "Reason": rv["reason"],
                    "Status": rv["status"].upper(),
                    "Created": str(rv["created_at"])[:16]
                })

            df_revoke = pd.DataFrame(revoke_data)
            st.dataframe(df_revoke, use_container_width=True, hide_index=True)

            st.divider()

            if pending_revokes:
                st.markdown("**⏳ Pending Revocation Requests**")

                for rev_req in pending_revokes:
                    with st.expander(f"Request #{rev_req['id']} - Certificate #{rev_req['certificate_id']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**User ID:** {rev_req['user_id']}")
                            st.write(f"**Reason:** {rev_req['reason']}")
                        with col2:
                            st.write(f"**Requested:** {str(rev_req['created_at'])[:19]}")
                            st.write(f"**Status:** {rev_req['status'].upper()}")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Approve", key=f"approve_revoke_{rev_req['id']}"):
                                try:
                                    api_client.approve_revocation_request(rev_req["id"])
                                    st.success(f"Revocation request #{rev_req['id']} approved – certificate revoked.")
                                    st.rerun()
                                except http_requests.HTTPError as e:
                                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                                    st.error(f"Error: {detail}")
                        with col2:
                            if st.button("❌ Reject", key=f"reject_revoke_{rev_req['id']}"):
                                try:
                                    api_client.reject_revocation_request(rev_req["id"])
                                    st.info(f"Revocation request #{rev_req['id']} rejected – certificate remains active.")
                                    st.rerun()
                                except http_requests.HTTPError as e:
                                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                                    st.error(f"Error: {detail}")
