import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import api_client
import requests as http_requests


def renew_certificates():

    # Initialize session state
    if "renewed_certificates" not in st.session_state:
        st.session_state.renewed_certificates = []

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("🔄 Renew Certificates")
    st.markdown("Renew expiring or expired certificates for users")
    st.divider()

    # ── Fetch certificates from backend ──
    try:
        all_certificates = api_client.get_all_certificates()
    except http_requests.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return
    except http_requests.HTTPError as e:
        st.error(f"Backend error: {e}")
        return

    now = datetime.utcnow()

    # Classify active certs as expiring soon (< 30 days) or not
    active_certs = [c for c in all_certificates if c["status"] == "approved"]
    expiring_soon = []
    for c in active_certs:
        try:
            valid_to = datetime.fromisoformat(str(c["valid_to"]).replace("T", " ").split(".")[0])
            days_left = (valid_to - now).days
            if days_left <= 30:
                expiring_soon.append(c)
        except Exception:
            pass

    expired_certs = [c for c in all_certificates if c["status"] == "expired"]

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏰ Expiring Soon", len(expiring_soon))
    with col2:
        st.metric("❌ Expired", len(expired_certs))
    with col3:
        st.metric("🔄 Total Active", len(active_certs))
    with col4:
        st.metric("✅ Renewed", len(st.session_state.renewed_certificates))

    st.divider()

    tab1, tab2 = st.tabs(["🔄 Renew Certificate", "📋 Renewal History"])

    with tab1:
        st.subheader("Select Certificate to Renew")

        renewable = expiring_soon + expired_certs + active_certs

        if not renewable:
            st.info("No certificates available to renew.")
        else:
            cert_options = []
            for c in renewable:
                try:
                    valid_to = datetime.fromisoformat(str(c["valid_to"]).replace("T", " ").split(".")[0])
                    days_left = (valid_to - now).days
                    label = f"Cert #{c['id']} - User {c['user_id']} - {str(c['valid_to'])[:10]} ({days_left}d left)"
                except Exception:
                    label = f"Cert #{c['id']} - User {c['user_id']}"
                cert_options.append(label)

            selected_idx = st.selectbox(
                "Choose a certificate to renew:",
                range(len(renewable)),
                format_func=lambda i: cert_options[i],
                key="renew_cert_select"
            )

            selected_cert = renewable[selected_idx]

            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Certificate ID:** {selected_cert['id']}")
                st.write(f"**User ID:** {selected_cert['user_id']}")
                st.write(f"**Serial Number:** `{selected_cert['serial_number']}`")
                st.write(f"**Status:** {selected_cert['status'].upper()}")

            with col2:
                st.write(f"**Valid From:** {str(selected_cert['valid_from'])[:10]}")
                st.write(f"**Valid To:** {str(selected_cert['valid_to'])[:10]}")
                try:
                    valid_to_dt = datetime.fromisoformat(str(selected_cert["valid_to"]).replace("T", " ").split(".")[0])
                    days_left = (valid_to_dt - now).days
                    st.write(f"**Days Until Expiry:** {days_left} day(s)")
                except Exception:
                    pass

            # Show current PEM
            with st.expander("📄 Current Certificate (PEM)"):
                st.code(selected_cert["cert_pem"], language="text")

            st.divider()

            st.subheader("Renewal Configuration")

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

            with col2:
                hash_algorithm = st.selectbox(
                    "Hash Algorithm:",
                    options=["SHA256", "SHA384", "SHA512"],
                    index=0,
                    key="renew_hash_algorithm"
                )

            st.divider()

            new_expiry = datetime.utcnow() + timedelta(days=validity_days)

            st.markdown(f"""
            <div style="background-color: #2d3748; border-left: 4px solid #9f7aea; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="font-weight: bold; color: #9f7aea; margin-bottom: 10px;">🔄 Renewal Summary</div>
            <div style="color: #e0e0e0; font-size: 14px;">
            <div style="margin: 5px 0;">✅ Certificate ID: <strong>{selected_cert['id']}</strong></div>
            <div style="margin: 5px 0;">✅ New validity: <strong>{validity_days} days</strong></div>
            <div style="margin: 5px 0;">✅ New expiry: <strong>{new_expiry.strftime('%Y-%m-%d')}</strong></div>
            <div style="margin: 5px 0;">✅ Hash algorithm: <strong>{hash_algorithm}</strong></div>
            </div>
            </div>
            """, unsafe_allow_html=True)

            confirm_renew = st.checkbox("I confirm the certificate renewal", key="confirm_renew_cert")

            if st.button(
                "🔄 Renew Certificate",
                disabled=not confirm_renew,
                key="btn_renew_cert",
                use_container_width=True
            ):
                with st.spinner("Renewing certificate..."):
                    try:
                        new_cert = api_client.admin_renew_certificate(
                            cert_id=selected_cert["id"],
                            validity_days=validity_days,
                            hash_alg=hash_algorithm
                        )
                        renewal_record = {
                            "original_cert_id": selected_cert["id"],
                            "new_cert_id": new_cert["id"],
                            "user_id": new_cert["user_id"],
                            "serial_number": new_cert["serial_number"],
                            "new_valid_to": str(new_cert["valid_to"])[:10],
                            "hash_algorithm": hash_algorithm,
                            "timestamp": datetime.now()
                        }
                        st.session_state.renewed_certificates.append(renewal_record)

                        st.success(f"""
                        ✅ Certificate Renewed Successfully!

                        **Renewal Details:**
                        - **Original Certificate ID:** {selected_cert['id']}
                        - **New Certificate ID:** {new_cert['id']}
                        - **New Serial Number:** {new_cert['serial_number']}
                        - **Valid From:** {str(new_cert['valid_from'])[:10]}
                        - **Valid To:** {str(new_cert['valid_to'])[:10]}
                        - **Hash Algorithm:** {hash_algorithm}
                        """)

                        st.download_button(
                            label="📥 Download New Certificate",
                            data=new_cert["cert_pem"],
                            file_name=f"cert_{new_cert['id']}_renewed.pem",
                            mime="application/x-pem-file"
                        )

                    except http_requests.HTTPError as e:
                        detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                        st.error(f"❌ Error: {detail}")
                    except http_requests.ConnectionError:
                        st.error("❌ Cannot connect to backend.")

    with tab2:
        st.subheader("Certificate Renewal History")

        if not st.session_state.renewed_certificates:
            st.info("No certificate renewals yet this session.")
        else:
            history_data = [
                {
                    "Original ID": r["original_cert_id"],
                    "New ID": r["new_cert_id"],
                    "User ID": r["user_id"],
                    "New Valid To": r["new_valid_to"],
                    "Algorithm": r["hash_algorithm"],
                    "Renewed": r["timestamp"].strftime('%Y-%m-%d %H:%M')
                }
                for r in st.session_state.renewed_certificates
            ]
            df_history = pd.DataFrame(history_data)
            st.dataframe(df_history, use_container_width=True, hide_index=True)
