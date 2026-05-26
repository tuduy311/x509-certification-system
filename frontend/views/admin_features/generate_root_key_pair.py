import streamlit as st
from datetime import datetime
import api.api_client as api_client
import requests as http_requests

from styles.dashboard import Dashboard_CSS


def _load_options():
    """Load algorithms and key lengths from backend once per session."""
    if "asymmetric_algos" not in st.session_state or "key_lengths" not in st.session_state:
        try:
            all_opts = api_client.get_all_options()
            st.session_state.asymmetric_algos = [a["name"] for a in all_opts["asymmetric_algorithms"]]
            st.session_state.key_lengths = all_opts["key_lengths"]
            st.session_state.options_load_error = None
        except Exception as e:
            st.session_state.asymmetric_algos = []
            st.session_state.key_lengths = []
            st.session_state.options_load_error = str(e)


def _load_ca_status():
    """Fetch CA status from backend once per session (or after a generate action)."""
    if "ca_status" not in st.session_state:
        try:
            st.session_state.ca_status = api_client.get_ca_status()
        except Exception:
            st.session_state.ca_status = {"key_exists": False, "cert_exists": False}


def generate_root_key_pair():
    st.markdown(Dashboard_CSS, unsafe_allow_html=True)

    # ── Session state ──
    if "root_key_history" not in st.session_state:
        st.session_state.root_key_history = []
    if "root_key_success_msg" not in st.session_state:
        st.session_state.root_key_success_msg = None

    # Load options and CA status (cached in session, no re-request on widget changes)
    _load_options()
    _load_ca_status()

    # ── Back button ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    # ── Header ──
    st.markdown("""
    <div class="admin-card">
        <div class="admin-title">🔑 Generate Root CA Key Pair</div>
        <div class="admin-content">
            Create a new RSA or ECC private key for the Root Certificate Authority.
            The key is stored securely on the server inside <code>key_CA/</code> and
            is <strong>never</strong> transmitted to the browser.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── CA Status banner (from cached session state) ──
    status  = st.session_state.ca_status
    key_ok  = status.get("key_exists", False)
    cert_ok = status.get("cert_exists", False)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if key_ok:
            st.success("🔑 Root CA key already exists on server (`key_CA/root_ca.key`)")
        else:
            st.warning("⚠️ No Root CA key found – generate one below.")
    with col_s2:
        if cert_ok:
            st.success("📜 Root CA certificate exists (`cert_CA/root_ca.crt`)")
        else:
            st.info("ℹ️ No certificate yet – generate it after creating the key.")

    st.divider()

    tab1, tab2 = st.tabs(["🔑 Generate New Key", "📋 Generation History"])

    # ─────────────────────────────── TAB 1 ────────────────────────────────────
    with tab1:
        st.subheader("New Root CA Key Pair")

        # Show error if backend options could not be loaded
        if st.session_state.get("options_load_error"):
            st.error(f"❌ Failed to load algorithm options from backend: {st.session_state.options_load_error}")
            st.stop()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Key Parameters:**")

            algorithm = st.selectbox(
                "Asymmetric Algorithm",
                options=st.session_state.asymmetric_algos,
                key="rk_algo"
            )

            # Filter key lengths dynamically based on selected algorithm
            algo_lengths = [
                kl["value"] for kl in st.session_state.key_lengths
                if kl["algo_name"].upper() == algorithm.upper()
            ]
            if not algo_lengths:
                st.warning(f"⚠️ No key sizes found for {algorithm} in the database.")
                return

            key_size = st.selectbox(
                "Key Size (bits)",
                options=algo_lengths,
                index=0,
                key="rk_key_size"
            )

        with col2:
            st.markdown("**Configuration Summary:**")
            st.markdown(f"""
            <div style="background-color:#2d3748; border-left:4px solid #4299e1;
                        border-radius:5px; padding:15px; margin:10px 0;">
            <div style="color:#e0e0e0; font-size:14px;">
            <div style="margin:5px 0;"><strong>Algorithm:</strong> {algorithm}</div>
            <div style="margin:5px 0;"><strong>Key Size:</strong> {key_size} bits</div>
            <div style="margin:5px 0;"><strong>Storage:</strong> Server → <code>key_CA/root_ca.key</code></div>
            <div style="margin:5px 0;"><strong>Key returned to browser:</strong> ❌ No (server-side only)</div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        with st.expander("🛡️ Security Considerations"):
            st.markdown("""
            - The private key is written **only** to the server file system (`key_CA/root_ca.key`)
            - The key is **never** returned to the browser or logged
            - Generating a new key will **overwrite** any existing `root_ca.key` file
            - After generating the key, use **Generate Root Certificate** to create the CA certificate
            - Store offline backups of the key file in a Hardware Security Module (HSM) or encrypted vault
            """)

        st.divider()

        confirm = st.checkbox(
            "⚠️ I understand this will overwrite any existing root CA key on the server",
            key="rk_confirm"
        )

        if st.button(
            "🔑 Generate & Save Key Pair",
            disabled=not confirm,
            use_container_width=True,
            type="primary",
            key="btn_gen_root_key"
        ):
            with st.spinner(f"Generating {algorithm} {key_size}-bit key pair on server…"):
                try:
                    result = api_client.generate_root_key(algo=algorithm, key_size=key_size)

                    record = {
                        "algorithm": result.get("algorithm", algorithm),
                        "key_size":  result.get("key_size",  key_size),
                        "msg":       result.get("msg", "Success"),
                        "timestamp": datetime.now(),
                    }
                    st.session_state.root_key_history.append(record)

                    # Update CA status in session without re-requesting anything else
                    st.session_state.ca_status["key_exists"] = True

                    st.session_state.root_key_success_msg = (
                        f"✅ **Root CA Key Pair Generated Successfully!**\n\n"
                        f"**Details:**\n"
                        f"- **Saved to:** `key_CA/root_ca.key` on server\n"
                        f"- **Generated:** {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"- **Server message:** {record['msg']}\n\n"
                        f"👉 **Next step:** Go to **Generate Root Certificate** to create the CA certificate using this key."
                    )

                except http_requests.HTTPError as e:
                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                    st.error(f"❌ Backend error: {detail}")
                    st.session_state.root_key_success_msg = None
                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend.")
                    st.session_state.root_key_success_msg = None

        # Show persistent success message (stays visible without rerun)
        if st.session_state.root_key_success_msg:
            st.success(st.session_state.root_key_success_msg)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if st.button(
            "➡️ Go to Generate Root Certificate",
            use_container_width=True,
            key="goto_gen_cert"
        ):
            st.session_state.current_feature = "generate_root_certificate"
            st.rerun()

    # ─────────────────────────────── TAB 2 ────────────────────────────────────
    with tab2:
        st.subheader("Key Generation History (This Session)")

        if not st.session_state.root_key_history:
            st.info("No root CA key pairs generated this session.")
        else:
            st.success(f"✅ {len(st.session_state.root_key_history)} key generation(s) recorded this session.")
            for idx, rec in enumerate(reversed(st.session_state.root_key_history), 1):
                n = len(st.session_state.root_key_history) - idx + 1
                with st.expander(f"🔑 Generation #{n} — {rec['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Algorithm:** {rec['algorithm']}")
                        st.write(f"**Key Size:** {rec['key_size']} bits")
                    with col2:
                        st.write(f"**Generated:** {rec['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Server response:** {rec['msg']}")

            st.divider()
            st.info("🗂️ Key files are stored on the server at `key_CA/root_ca.key`.")
