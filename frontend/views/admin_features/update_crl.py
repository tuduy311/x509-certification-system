import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import api.api_client as api_client
import requests as http_requests


def update_crl():

    # Initialize session state
    if "generated_crls" not in st.session_state:
        st.session_state.generated_crls = []

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("📋 Update Certificate Revocation List (CRL)")
    st.markdown("Generate and publish a new Certificate Revocation List")
    st.divider()

    # ── Fetch revoked certs from backend ──
    try:
        all_certs = api_client.get_all_certificates()
    except http_requests.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        all_certs = []
    except http_requests.HTTPError as e:
        st.error(f"Backend error: {e}")
        all_certs = []

    revoked_certs = [c for c in all_certs if c["status"] == "revoked"]

    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("❌ Revoked Certificates", len(revoked_certs))
    with col2:
        st.metric("📋 CRLs Generated", len(st.session_state.generated_crls))
    with col3:
        st.metric("✅ Total Active", len([c for c in all_certs if c["status"] == "approved"]))
    with col4:
        st.metric("📊 Total Certs", len(all_certs))

    st.divider()

    tab1, tab2 = st.tabs(["📝 Generate New CRL", "📋 CRL History"])

    with tab1:
        st.subheader("Generate New Certificate Revocation List")

        st.markdown("**📄 Revoked Certificates to Include**")

        if not revoked_certs:
            st.info("ℹ️ No revoked certificates found. The CRL will be empty.")
        else:
            crl_data = [
                {
                    "Certificate ID": c["id"],
                    "Serial Number": c["serial_number"],
                    "User ID": c["user_id"],
                    "Valid To": str(c["valid_to"])[:10],
                    "Created": str(c["created_at"])[:10]
                }
                for c in revoked_certs
            ]
            df_revoked = pd.DataFrame(crl_data)
            st.dataframe(df_revoked, use_container_width=True, hide_index=True)

        st.divider()

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
            - CRL Authority Signature
            """)

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
            with st.spinner("Generating Certificate Revocation List on server..."):
                try:
                    result = api_client.generate_crl(
                        validity_days=validity_days,
                        hash_alg=hash_algorithm
                    )
                    crl_pem = result.get("crl_pem", "")

                    new_crl = {
                        "id": len(st.session_state.generated_crls) + 1,
                        "generated_at": datetime.now(),
                        "validity_days": validity_days,
                        "hash_algorithm": hash_algorithm,
                        "revoked_count": len(revoked_certs),
                        "crl_pem": crl_pem
                    }
                    st.session_state.generated_crls.append(new_crl)

                    st.success(f"""
                    ✅ Certificate Revocation List Generated Successfully!

                    **CRL Details:**
                    - **Generated:** {new_crl['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}
                    - **Valid Until:** {(new_crl['generated_at'] + timedelta(days=validity_days)).strftime('%Y-%m-%d %H:%M:%S')}
                    - **Hash Algorithm:** {hash_algorithm}
                    - **Revoked Certificates:** {len(revoked_certs)}

                    **⚠️ Next Steps:**
                    1. Download the CRL and publish it to your distribution endpoints
                    2. Notify subscribers of the CRL update
                    """)

                    if crl_pem:
                        st.markdown("**📄 Generated CRL (PEM Format):**")
                        st.code(crl_pem, language="text")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📥 Download CRL (PEM)",
                                data=crl_pem,
                                file_name=f"crl_{new_crl['id']}_{new_crl['generated_at'].strftime('%Y%m%d')}.pem",
                                mime="application/x-pem-file"
                            )
                        with col2:
                            st.info("💡 Publish this CRL to your HTTP/LDAP distribution points.")

                except http_requests.HTTPError as e:
                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                    st.error(f"❌ Error generating CRL: {detail}")
                    st.info("💡 Make sure the Root CA has been set up first (Generate Root Certificate).")
                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend.")

    with tab2:
        st.subheader("CRL Generation History")

        if not st.session_state.generated_crls:
            st.info("No CRL generation history yet.")
        else:
            for crl in reversed(st.session_state.generated_crls):
                with st.expander(f"📝 CRL #{crl['id']} — Generated {crl['generated_at'].strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Generated:** {crl['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Validity:** {crl['validity_days']} days")
                        st.write(f"**Hash Algorithm:** {crl['hash_algorithm']}")
                    with col2:
                        st.write(f"**Revoked Certs:** {crl['revoked_count']}")
                        valid_until = crl['generated_at'] + timedelta(days=crl['validity_days'])
                        st.write(f"**Valid Until:** {valid_until.strftime('%Y-%m-%d %H:%M:%S')}")

                    if crl.get("crl_pem"):
                        st.markdown("**CRL Content (PEM):**")
                        st.markdown(f"""
                        <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto; max-height: 200px; overflow-y: auto;">
                        <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{crl['crl_pem']}</pre>
                        </div>
                        """, unsafe_allow_html=True)

                        st.download_button(
                            label="📥 Download CRL",
                            data=crl["crl_pem"],
                            file_name=f"crl_{crl['id']}.pem",
                            mime="application/x-pem-file",
                            key=f"download_history_{crl['id']}"
                        )
