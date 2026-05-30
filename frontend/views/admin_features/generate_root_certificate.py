import streamlit as st
from datetime import datetime
import api.api_client as api_client
import requests as http_requests
from api.helpers import BackendError

from styles.dashboard import Dashboard_CSS


def _load_hash_algos():
    """Load hash algorithms from backend once per session."""
    if "hash_algos" not in st.session_state:
        try:
            all_opts = api_client.get_all_options()
            st.session_state.hash_algos = [h["name"] for h in all_opts["hash_algorithms"]]
            st.session_state.hash_algos_load_error = None
        except Exception as e:
            st.session_state.hash_algos = []
            st.session_state.hash_algos_load_error = str(e)


def _load_ca_status():
    """Always fetch CA status fresh from backend to reflect actual file existence."""
    
    try:
        st.session_state.ca_status = api_client.get_ca_status()
    except Exception:
        st.session_state.ca_status = {"key_exists": False, "cert_exists": False}


def generate_root_certificate():
    st.markdown(Dashboard_CSS, unsafe_allow_html=True)

    # ── Session state ──
    if "root_cert_history" not in st.session_state:
        st.session_state.root_cert_history = []
    if "root_cert_success_msg" not in st.session_state:
        st.session_state.root_cert_success_msg = None
    if "_show_root_cert_msg" not in st.session_state:
        st.session_state._show_root_cert_msg = False

    # Load hash algos and CA status (cached in session, no re-request on widget changes)
    _load_hash_algos()
    _load_ca_status()

    # ── Back button ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    # ── Header ──
    st.markdown("""
    <div class="admin-card">
        <div class="admin-title">📜 Generate Root CA Certificate</div>
        <div class="admin-content">
            Read the Root CA private key stored in <code>key_CA/root_ca.key</code>,
            build a self-signed X.509 certificate, and save it to
            <code>cert_CA/root_ca.crt</code> on the server.<br>
            <strong>The Root CA key pair must exist before running this step.</strong>
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
            st.success("🔑 Root CA key found – ready to generate certificate.")
        else:
            st.error("❌ Root CA key NOT found. Generate the key pair first.")
    with col_s2:
        if cert_ok:
            st.warning("⚠️ A certificate already exists in server – generating will overwrite it.")
        else:
            st.info("ℹ️ No certificate yet – fill in the form below and generate one.")

    st.divider()

    tab1, tab2 = st.tabs(["📜 Generate Certificate", "📋 Session History"])

    # ─────────────────────────────── TAB 1 ────────────────────────────────────
    with tab1:
        st.subheader("New Root CA Certificate")
        st.markdown("Configure the parameters for the self-signed Root CA certificate.")

        if not key_ok:
            st.warning("⚠️ Please generate the Root CA key pair first before proceeding.")
            if st.button("➡️ Go to Generate Root Key Pair", use_container_width=True, key="goto_gen_key"):
                st.session_state.current_feature = "generate_root_key_pair"
                st.rerun()
            return  # Block form if no key exists

        # Show error if backend options could not be loaded
        if st.session_state.get("hash_algos_load_error"):
            st.error(f"❌ Failed to load hash algorithm options from backend: {st.session_state.hash_algos_load_error}")
            st.stop()

        st.markdown("**Certificate Parameters:**")

        validity_days = st.number_input(
            "Validity Period (days):",
            min_value=365,
            max_value=36500,
            value=3650,
            step=365,
            key="rc_validity"
        )

        hash_algorithm = st.selectbox(
            "Hash Algorithm:",
            options=st.session_state.hash_algos,
            index=0,
            key="rc_hash_alg"
        )

        st.divider()

        # Configuration summary (reactive to widget values, no request needed)
        st.markdown(f"""
        <div style="background-color:#2d3748; border-left:4px solid #48bb78;
                    border-radius:5px; padding:15px; margin:15px 0;">
        <div style="font-weight:bold; color:#48bb78; margin-bottom:10px;">✓ Certificate Configuration</div>
        <div style="color:#e0e0e0; font-size:14px;">
        <div style="margin:5px 0;">✅ Key source: <strong>key_CA/root_ca.key</strong> (server-side)</div>
        <div style="margin:5px 0;">✅ Type: <strong>Self-signed Root CA</strong></div>
        <div style="margin:5px 0;">✅ Validity: <strong>{validity_days} days ({validity_days/365:.1f} years)</strong></div>
        <div style="margin:5px 0;">✅ Hash Algorithm: <strong>{hash_algorithm}</strong></div>
        <div style="margin:5px 0;">✅ Output: <strong>cert_CA/root_ca.crt</strong> (server-side)</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🛡️ Security & Compliance"):
            st.markdown("""
            **Security Best Practices:**
            - Root CA certificate should be highly protected
            - Store private key in HSM (Hardware Security Module)
            - Use strong key size (minimum 2048 bits for RSA, minimum 256 bits for ECC)
            - Set appropriate validity period (10 years recommended for Root CA)

            **Compliance Standards:**
            - RFC 5280 – Internet X.509 Public Key Infrastructure
            - CA/Browser Forum Baseline Requirements
            """)

        confirm_generate = st.checkbox(
            "I understand that creating a new certificate will overwrite the existing certificate",
            key="rc_confirm"
        )

        if st.button(
            "📜 Generate & Save Certificate",
            disabled=not confirm_generate,
            use_container_width=True,
            type="primary",
            key="btn_gen_root_cert"
        ):
            with st.spinner("Reading key and generating Root CA certificate on server…"):
                try:
                    result = api_client.generate_root_cert(
                        validity_days=int(validity_days),
                        hash_alg=hash_algorithm
                    )

                    record = {
                        "validity_days": result.get("validity_days", validity_days),
                        "hash_alg":      result.get("hash_alg", hash_algorithm),
                        "msg":           result.get("msg", "Success"),
                        "timestamp":     datetime.now(),
                    }
                    st.session_state.root_cert_history.append(record)

                    # Update CA status in session without re-requesting anything else
                    st.session_state.ca_status["cert_exists"] = True

                    st.session_state.root_cert_success_msg = (
                        f"✅ **Root CA Certificate Generated Successfully!**\n\n"
                        f"**Certificate Details:**\n"
                        f"- **Validity:** {record['validity_days']} days (~{record['validity_days']/365:.1f} years)\n"
                        f"- **Hash Algorithm:** {record['hash_alg']}\n"
                        f"- **Saved to:** `cert_CA/root_ca.crt` on server\n"
                        f"- **Generated:** {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"- **Server message:** {record['msg']}\n\n"
                        f"**⚠️ Important:**\n"
                        f"1. The Root CA cert is saved to `cert_CA/root_ca.crt` on the server\n"
                        f"2. Backup the `key_CA/root_ca.key` file in a secure offline location\n"
                        f"3. Keep the private key confidential – it signs ALL issued certificates"
                    )
                    st.session_state._show_root_cert_msg = True

                except BackendError:
                    st.session_state.root_cert_success_msg = None
                except http_requests.HTTPError as e:
                    if e.response is not None:
                        detail = e.response.json().get("detail", str(e))
                        st.error(f"❌ {detail}")
                    else:
                        st.error(f"❌ Error: {str(e)}")
                    st.session_state.root_cert_success_msg = None
                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend.")
                    st.session_state.root_cert_success_msg = None

        if st.session_state._show_root_cert_msg and st.session_state.root_cert_success_msg:
            st.success(st.session_state.root_cert_success_msg)
            st.session_state._show_root_cert_msg = False
            st.session_state.root_cert_success_msg = None

    # ─────────────────────────────── TAB 2 ────────────────────────────────────
    with tab2:
        st.subheader("Certificate Generation History (This Session)")

        if not st.session_state.root_cert_history:
            st.info("No Root CA certificates generated this session.")
        else:
            for idx, cert in enumerate(reversed(st.session_state.root_cert_history), 1):
                n = len(st.session_state.root_cert_history) - idx + 1
                with st.expander(f"📜 Generation #{n} — {cert['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Hash Algorithm:** {cert['hash_alg']}")
                        st.write(f"**Validity:** {cert['validity_days']} days")
                    with col2:
                        st.write(f"**Generated:** {cert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Server response:** {cert['msg']}")

            st.divider()
            st.info("🗂️ Certificate files are stored on the server at `cert_CA/root_ca.crt`.")
