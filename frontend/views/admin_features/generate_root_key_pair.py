import streamlit as st


def generate_root_key_pair():

    # Initialize session state
    if "generated_key_pairs" not in st.session_state:
        st.session_state.generated_key_pairs = []

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("🔑 Generate Root Key Pair")
    st.markdown("Create a new Root Key Pair for the Certificate Authority")
    st.divider()

    # Create two tabs
    tab1, tab2 = st.tabs(["🔑 Generate New", "📋 Existing Key Pairs"])

    with tab1:
        st.subheader("Generate New Root Key Pair")

        st.info("""
        **ℹ️ How key generation works in this system:**

        The Root CA key pair is generated **together** with the Root CA certificate
        when you use the **Generate Root Certificate** feature.

        This is standard CA practice – the private key and self-signed certificate
        are created in a single atomic operation to ensure they are cryptographically bound.

        👉 Go to **System → Generate Root Certificate** to generate a new key pair + certificate.
        """)

        col1, col2 = st.columns(2)

        with col1:
            algorithm = st.radio(
                "Key Algorithm (reference):",
                options=["RSA"],
                key="root_key_algo"
            )

            key_size = st.selectbox(
                "Key Size (bits):",
                options=[2048, 3072, 4096],
                index=0,
                key="rsa_key_size"
            )

        with col2:
            st.markdown("**Configuration Summary:**")
            st.markdown(f"""
            <div style="background-color: #2d3748; border-left: 4px solid #4299e1; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="color: #e0e0e0; font-size: 14px;">
            <div style="margin: 5px 0;"><strong>Algorithm:</strong> {algorithm}</div>
            <div style="margin: 5px 0;"><strong>Key Size:</strong> {key_size} bits</div>
            <div style="margin: 5px 0;"><strong>Generated via:</strong> Generate Root Certificate page</div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        if st.button(
            "➡️ Go to Generate Root Certificate",
            use_container_width=True,
            key="goto_gen_cert"
        ):
            st.session_state.current_feature = "generate_root_certificate"
            st.rerun()

        st.divider()

        with st.expander("🛡️ Security Considerations"):
            st.markdown("""
            - **Key Storage**: Store root keys in secure Hardware Security Module (HSM)
            - **Backup**: Create offline backups and store in vault
            - **Access Control**: Restrict key access to authorized personnel only
            - **Monitoring**: Enable audit logs for all key operations
            - **Rotation**: Plan periodic key rotation schedule
            """)

    with tab2:
        st.subheader("Root CA Generation History")

        # Show history from generate_root_certificate session state
        history = st.session_state.get("generated_root_certs", [])

        if not history:
            st.info("No root CA key pairs generated this session. Use 'Generate Root Certificate' to create one.")
        else:
            st.success(f"✅ {len(history)} root CA generation(s) recorded this session.")

            for idx, cert in enumerate(reversed(history), 1):
                with st.expander(f"🔑 Generation #{len(history) - idx + 1} — {cert['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Key Size:** {cert['key_size']} bits")
                        st.write(f"**Hash Algorithm:** {cert['hash_alg']}")
                    with col2:
                        st.write(f"**Validity:** {cert['validity_days']} days")
                        st.write(f"**Generated At:** {cert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Server response:** {cert['msg']}")

            st.divider()
            st.markdown("**Legend:** Key pair files are stored on the server at the path set in `ROOT_CA_PATH` (.env)")
