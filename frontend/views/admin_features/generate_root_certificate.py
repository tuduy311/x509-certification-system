import streamlit as st
from datetime import datetime
import api_client
import requests as http_requests


def generate_root_certificate():

    # Initialize session state
    if "generated_root_certs" not in st.session_state:
        st.session_state.generated_root_certs = []

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("📜 Generate Root Certificate")
    st.markdown("Create a new Root Certificate Authority (CA) certificate")
    st.divider()

    # ── Fetch option lists from backend once per visit ──
    if "asymmetric_algos" not in st.session_state or st.session_state.asymmetric_algos is None:
        try:
            st.session_state.asymmetric_algos = [alg["name"] for alg in api_client.get_asymmetric_algorithms()]
        except Exception:
            st.session_state.asymmetric_algos = ["RSA", "ECC"]

    if "key_lengths" not in st.session_state or st.session_state.key_lengths is None:
        try:
            st.session_state.key_lengths = api_client.get_key_lengths()
        except Exception:
            st.session_state.key_lengths = [
                {"value": 2048, "algo_name": "RSA"},
                {"value": 3072, "algo_name": "RSA"},
                {"value": 4096, "algo_name": "RSA"},
                {"value": 256, "algo_name": "ECC"},
                {"value": 384, "algo_name": "ECC"},
                {"value": 521, "algo_name": "ECC"},
            ]

    # Stats from session history
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📦 Generated This Session", len(st.session_state.generated_root_certs))
    with col2:
        st.info("The Root CA key and certificate are saved on the **server** at the path configured in `.env` (`ROOT_CA_PATH`).")

    st.divider()

    # Two tabs
    tab1, tab2 = st.tabs(["📜 Generate New", "📋 Session History"])

    with tab1:
        st.subheader("Generate New Root CA Certificate")
        st.markdown("Configure parameters for the new root CA certificate")


        st.markdown("**Certificate Parameters**")

        algorithm = st.selectbox(
            "Asymmetric Algorithm:",
            options=st.session_state.asymmetric_algos,
            key="root_cert_algo"
        )

        # Filter key sizes based on selected algorithm from DB
        algo_key_lengths = [kl["value"] for kl in st.session_state.key_lengths if kl["algo_name"].upper() == algorithm.upper()]
        if not algo_key_lengths:
            algo_key_lengths = [2048, 3072, 4096] if algorithm == "RSA" else [256, 384, 521]

        key_size = st.selectbox(
            "Key Size (bits):",
            options=algo_key_lengths,
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

        st.divider()

        # Configuration summary box
        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #48bb78; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #48bb78; margin-bottom: 10px;">✓ Certificate Configuration</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0;">✅ Self-signed Root CA certificate will be created</div>
        <div style="margin: 5px 0;">✅ Algorithm: <strong>{algorithm}</strong></div>
        <div style="margin: 5px 0;">✅ Key size: <strong>{key_size} bits</strong></div>
        <div style="margin: 5px 0;">✅ Certificate will be valid for <strong>{validity_days} days</strong></div>
        <div style="margin: 5px 0;">✅ Hash algorithm: <strong>{hash_algorithm}</strong></div>
        <div style="margin: 5px 0;">✅ Private key will be securely stored on the server</div>
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
            with st.spinner("Generating root CA certificate and key pair on server..."):
                try:
                    result = api_client.setup_root_ca(
                        algo=algorithm,
                        key_size=key_size,
                        validity_days=validity_days,
                        hash_alg=hash_algorithm
                    )
                    new_cert = {
                        "algo": algorithm,
                        "key_size": key_size,
                        "validity_days": validity_days,
                        "hash_alg": hash_algorithm,
                        "timestamp": datetime.now(),
                        "msg": result.get("msg", "Success")
                    }
                    st.session_state.generated_root_certs.append(new_cert)

                    st.success(f"""
                    ✅ Root CA Certificate Generated Successfully!

                    **Certificate Details:**
                    - **Asymmetric Algorithm:** {algorithm}
                    - **Key Size:** {key_size} bits
                    - **Hash Algorithm:** {hash_algorithm}
                    - **Validity:** {validity_days} days (~{validity_days/365:.1f} years)
                    - **Generated:** {new_cert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                    - **Server message:** {new_cert['msg']}

                    **⚠️ Important:**
                    1. The Root CA key and cert are saved on the server (ROOT_CA_PATH in .env)
                    2. Backup the `.key` file in a secure offline location
                    3. Keep the private key confidential – it signs ALL certificates
                    """)

                except http_requests.HTTPError as e:
                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                    st.error(f"❌ Error: {detail}")
                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend.")

        st.divider()
        with st.expander("🛡️ Security & Compliance"):
            st.markdown("""
            **Security Best Practices:**
            - Root CA certificate should be highly protected
            - Store private key in HSM (Hardware Security Module)
            - Use strong key size (minimum 2048 bits for RSA, minimum 256 bits for ECC)
            - Set appropriate validity period (10 years recommended)
            - Enable all critical extensions

            **Compliance Standards:**
            - RFC 5280 - Internet X.509 Public Key Infrastructure
            - CA/Browser Forum Baseline Requirements
            """)

    with tab2:
        st.subheader("Root CA Generation History (This Session)")

        if not st.session_state.generated_root_certs:
            st.info("No Root CA certificates generated this session.")
        else:
            for idx, cert in enumerate(reversed(st.session_state.generated_root_certs), 1):
                with st.expander(f"📜 Generation #{len(st.session_state.generated_root_certs) - idx + 1} — {cert['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Algorithm:** {cert['algo']}")
                        st.write(f"**Key Size:** {cert['key_size']} bits")
                    with col2:
                        st.write(f"**Hash Algorithm:** {cert['hash_alg']}")
                        st.write(f"**Validity:** {cert['validity_days']} days")
                    st.write(f"**Generated:** {cert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Server response:** {cert['msg']}")
