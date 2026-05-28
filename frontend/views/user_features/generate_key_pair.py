import streamlit as st
from datetime import datetime
import api.api_client as api_client
import requests as http_requests

# Key pair is generated entirely on the client side
from crypto import generate_key_pair as _crypto_generate_key_pair, serialize_keys

def generate_key_pair():
    # Initialize session state for single-session private key downloads
    if "last_generated_key" not in st.session_state:
        st.session_state.last_generated_key = None

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("🔑 Generate Key Pair")
    st.markdown("Generate a new public/private key pair for certificate signing requests")
    st.divider()

    # ── Load all lookup options from backend in a single request ──
    options_loaded = all(k in st.session_state for k in ["asymmetric_algos", "key_lengths"])
    if not options_loaded:
        try:
            all_opts = api_client.get_all_options()
            st.session_state.asymmetric_algos = [alg["name"] for alg in all_opts["asymmetric_algorithms"]]
            st.session_state.key_lengths = all_opts["key_lengths"]
        except Exception as e:
            st.session_state.asymmetric_algos = ["RSA", "ECC"]
            st.session_state.key_lengths = [
                {"value": 2048, "algo_name": "RSA"},
                {"value": 3072, "algo_name": "RSA"},
                {"value": 4096, "algo_name": "RSA"},
                {"value": 256, "algo_name": "ECC"},
                {"value": 384, "algo_name": "ECC"},
                {"value": 521, "algo_name": "ECC"},
            ]

    tab1, tab2 = st.tabs(["🔨 Generate New Key", "📋 My Key Pairs"])

    with tab1:
        st.subheader("Create New Key Pair")

        col1, col2 = st.columns(2)

        with col1:
            algorithm = st.selectbox(
                "Algorithm:",
                options=st.session_state.asymmetric_algos,
                key="key_algo"
            )

            # Filter key sizes based on selected algorithm from DB
            algo_key_lengths = [kl["value"] for kl in st.session_state.key_lengths if kl["algo_name"].upper() == algorithm.upper()]
            if not algo_key_lengths:
                algo_key_lengths = [2048, 3072, 4096] if algorithm == "RSA" else [256, 384, 521]

            key_size = st.selectbox(
                "Key Size (bits):",
                options=algo_key_lengths,
                index=0,
                key="key_size"
            )

        with col2:
            st.markdown("**📝 Key Description (optional):**")
            key_description = st.text_area(
                "Description for this key pair:",
                placeholder="e.g., Main web server key, Backup key, Development key",
                height=80,
                key="key_desc"
            )

        st.divider()

        with st.expander("🔒 Security Considerations"):
            st.markdown("""
            - **Key Size:** Larger keys (3072, 4096 for RSA; 384, 521 for ECC) provide better security but slower performance
            - **Algorithm:** RSA is widely supported; ECC is more modern and efficient (with smaller key size)
            - **Private Key:** The private key is shown only ONCE – download it immediately!
            - **Backup:** Store your private key in a secure, offline location
            - **Rotation:** Regularly rotate keys and request revocations for old certs
            """)

        st.divider()

        # Generation summary
        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #4299e1; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #4299e1; margin-bottom: 10px;">🔐 Key Pair Summary</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0;"><strong>Algorithm:</strong> {algorithm}</div>
        <div style="margin: 5px 0;"><strong>Key Size:</strong> {key_size} bits</div>
        <div style="margin: 5px 0;"><strong>Description:</strong> {key_description if key_description else 'Not specified'}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Key Pair", use_container_width=True, key="btn_generate_key"):
            with st.spinner("Generating key pair locally and saving public key..."):
                try:
                    # ── 1. Generate on the client (private key never leaves) ──
                    private_key_obj = _crypto_generate_key_pair(algorithm=algorithm, key_size=key_size)
                    private_key_pem, public_key_pem = serialize_keys(private_key_obj)

                    # ── 2. Upload only the public key to the backend ───────────
                    key_record = api_client.save_public_key(
                        algorithm=algorithm,
                        key_size=key_size,
                        pubkey_pem=public_key_pem,
                        description=key_description,
                    )

                    st.session_state.last_generated_key = {
                        "id": key_record["id"],
                        "algorithm": algorithm,
                        "private_key": private_key_pem,
                        "public_key": public_key_pem,
                        "key_size": key_size,
                        "description": key_description,
                        "fingerprint": key_record["fingerprint"],
                        "timestamp": datetime.now()
                    }

                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend.")
                except http_requests.HTTPError as e:
                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                    st.error(f"❌ Error: {detail}")
                except Exception as e:
                    st.error(f"❌ Key generation failed: {e}")

        # Render the result block if a key was generated in this session
        if st.session_state.last_generated_key is not None:
            last_key = st.session_state.last_generated_key

            st.divider()

            st.success(f"""
            ✅ Key Pair Generated Successfully!

            **Key Details:**
            - **Algorithm:** {last_key['algorithm']}
            - **Size:** {last_key['key_size']} bits
            - **SHA256 Fingerprint:** `{last_key['fingerprint']}`
            - **Generated:** {last_key['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

            ⚠️ **IMPORTANT:** Download your private key NOW! It will not be stored on the server and cannot be shown again.
            """)

            # Safe description for filename
            description_str = last_key['description'] or ""
            safe_description = description_str.replace(" ", "_")
            desc_prefix = f"{safe_description}_" if safe_description else ""

            # Download private key and public key
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Private Key",
                    data=last_key["private_key"],
                    file_name=f"{desc_prefix}private_key_{last_key['id']}.pem",
                    mime="application/x-pem-file",
                    help="Save your private key securely! This is the only time you can download it.",
                    key=f"dl_last_privkey_{last_key['id']}"
                )
            with col2:
                st.download_button(
                    label="📥 Download Public Key",
                    data=last_key["public_key"],
                    file_name=f"{desc_prefix}public_key_{last_key['id']}.pem",
                    mime="application/x-pem-file",
                    key=f"dl_last_pubkey_{last_key['id']}"
                )

            st.divider()

            with st.expander("🔑 View Public Key (PEM)"):
                st.code(last_key["public_key"], language="text")

            with st.expander("⚠️ View Private Key (PEM) – Sensitive!"):
                st.warning("Keep this key secret! Anyone with this key can impersonate you.")
                st.code(last_key["private_key"], language="text")

    with tab2:
        st.subheader("My Saved Key Pairs (From Database)")

        # Query real user key pairs from DB
        try:
            my_keys = api_client.get_my_keys()
        except Exception as e:
            st.error(f"Failed to load keys from database: {e}")
            my_keys = []

        if not my_keys:
            st.info("No key pairs found in your database. Use the 'Generate New Key' tab to create one.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔄 Total Keys", len(my_keys))
            with col2:
                latest_date = my_keys[-1]["created_at"]
                if isinstance(latest_date, str):
                    try:
                        latest_date = datetime.fromisoformat(latest_date.replace("Z", "+00:00")).strftime('%Y-%m-%d')
                    except Exception:
                        pass
                st.metric("📅 Latest Created", str(latest_date)[:10])
            with col3:
                st.metric("🟢 Active Status", len([k for k in my_keys if k["status"] == "active"]))

            st.divider()
            st.info("ℹ️ Private keys are only shown once at generation time and are never stored in the database. You can copy/download the public keys below.")

            for key in reversed(my_keys):
                created_str = key["created_at"]
                if isinstance(created_str, str):
                    try:
                        created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                        created_str = created_dt.strftime('%Y-%m-%d %H:%M')
                    except Exception:
                        pass

                with st.expander(f"🔑 Key #{key['id']} – {key['algorithm']} {key['key_size']} bits – {created_str}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Key ID:** {key['id']}")
                        st.write(f"**Algorithm:** {key['algorithm']}")
                        st.write(f"**Key Size:** {key['key_size']} bits")
                        st.write(f"**SHA256 Fingerprint:** `{key['fingerprint']}`")
                    with col2:
                        st.write(f"**Generated:** {created_str}")
                        st.write(f"**Description:** {key['description'] or 'None'}")
                        st.write(f"**Status:** `{key['status']}`")

                    if key.get("pubkey_pem"):
                        st.markdown("**🔑 Public Key (PEM):**")
                        st.code(key["pubkey_pem"], language="text")
                        st.download_button(
                            label="📥 Download Public Key",
                            data=key["pubkey_pem"],
                            file_name=f"public_key_{key['id']}.pem",
                            mime="application/x-pem-file",
                            key=f"dl_pubkey_{key['id']}"
                        )
