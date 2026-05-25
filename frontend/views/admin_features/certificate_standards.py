import streamlit as st
from datetime import datetime
import json
import api_client
import requests as http_requests

def _load_config() -> dict:
    """Fetch config from backend and return as dict[str,str]."""
    raw = api_client.get_config()
    if isinstance(raw, list):
        return {item["key"]: str(item["value"]) for item in raw}
    return {k: str(v) for k, v in raw.items()}


def certificate_standards():
    if "config_data" not in st.session_state:
        st.session_state.config_data = None  # will be loaded from backend
    if "config_changed" not in st.session_state:
        st.session_state.config_changed = {}
    if "config_save_error" not in st.session_state:
        st.session_state.config_save_error = None

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("🏛️ Certificate Standards")
    st.markdown("Configure default certificate parameters and security settings")
    st.divider()

    # ── Load config & option lists from backend once per visit ──
    if st.session_state.config_data is None:
        try:
            st.session_state.config_data = _load_config()
        except Exception as e:
            st.error(f"❌ Cannot connect to backend to fetch current configuration: {e}")
            st.session_state.config_data = {}

    # ── Load all lookup options from backend in a single request ──
    options_loaded = all(k in st.session_state for k in ["asymmetric_algos", "hash_algos", "key_lengths", "validity_options"])
    if not options_loaded:
        try:
            all_opts = api_client.get_all_options()
            st.session_state.asymmetric_algos = [alg["name"] for alg in all_opts["asymmetric_algorithms"]]
            st.session_state.hash_algos = [h["name"] for h in all_opts["hash_algorithms"]]
            st.session_state.key_lengths = all_opts["key_lengths"]
            st.session_state.validity_options = [opt["value"] for opt in all_opts["validity_options"]]
        except Exception as e:
            st.warning(f"⚠️ Failed to batch load lookup options: {e}. Using defaults.")
            st.session_state.asymmetric_algos = ["RSA", "ECC"]
            st.session_state.hash_algos = ["SHA256", "SHA384", "SHA512"]
            st.session_state.key_lengths = [
                {"value": 2048, "algo_name": "RSA"},
                {"value": 3072, "algo_name": "RSA"},
                {"value": 4096, "algo_name": "RSA"},
                {"value": 256, "algo_name": "ECC"},
                {"value": 384, "algo_name": "ECC"},
                {"value": 521, "algo_name": "ECC"},
            ]
            st.session_state.validity_options = [90, 365, 730, 3650]

    config = st.session_state.config_data

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚙️ Basic Settings",
        "🔒 Encryption",
        "📅 Validity",
        "🛠️ Advanced"
    ])

    # ── TAB 1: Basic Settings ──
    with tab1:
        st.subheader("Basic Certificate Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Default Settings:**")

            curr_hash = config.get("hash_algorithm", "SHA256")
            if curr_hash not in st.session_state.hash_algos:
                st.session_state.hash_algos.append(curr_hash)
            
            hash_algo = st.selectbox(
                "Default Hash Algorithm",
                st.session_state.hash_algos,
                index=st.session_state.hash_algos.index(curr_hash) if curr_hash in st.session_state.hash_algos else 0,
                key="hash_algo_input"
            )
            st.session_state.config_changed["hash_algorithm"] = hash_algo

            curr_ver = config.get("certificate_version", "3")
            versions_list = ["1", "2", "3"]
            if curr_ver not in versions_list:
                versions_list.append(curr_ver)
            versions_list = sorted(list(set(versions_list)))

            cert_version = st.selectbox(
                "Certificate Version",
                versions_list,
                index=versions_list.index(curr_ver) if curr_ver in versions_list else 2,
                key="cert_version_input"
            )
            st.session_state.config_changed["certificate_version"] = cert_version

        with col2:
            st.write("**Default Validity Period:**")

            # Default Validity selectbox from validity_options DB table
            val_opts = [str(x) for x in st.session_state.validity_options]
            curr_val = config.get("default_validity_days", "365")
            if curr_val not in val_opts:
                val_opts.append(curr_val)
            val_opts = sorted(list(set(val_opts)), key=int)

            default_validity = st.selectbox(
                "Default Validity (days)",
                val_opts,
                index=val_opts.index(curr_val) if curr_val in val_opts else 0,
                key="default_validity_input"
            )
            st.session_state.config_changed["default_validity_days"] = default_validity

            crl_update = st.number_input(
                "CRL Update Interval (days)",
                min_value=1, max_value=365,
                value=int(config.get("crl_update_days", 30)),
                step=1,
                key="crl_update_input"
            )
            st.session_state.config_changed["crl_update_days"] = str(crl_update)

    # ── TAB 2: Encryption ──
    with tab2:
        st.subheader("Encryption Algorithm Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Asymmetric Algorithms:**")

            enable_rsa = st.checkbox(
                "Enable RSA",
                value=config.get("enable_rsa") == "true",
                key="enable_rsa_input"
            )
            st.session_state.config_changed["enable_rsa"] = "true" if enable_rsa else "false"

            enable_ecc = st.checkbox(
                "Enable ECC",
                value=config.get("enable_ecc") == "true",
                key="enable_ecc_input"
            )
            st.session_state.config_changed["enable_ecc"] = "true" if enable_ecc else "false"

            curr_asym = config.get("asymmetric_algorithm", "RSA")
            if curr_asym not in st.session_state.asymmetric_algos:
                st.session_state.asymmetric_algos.append(curr_asym)

            asymmetric_algo = st.selectbox(
                "Default Asymmetric Algorithm",
                st.session_state.asymmetric_algos,
                index=st.session_state.asymmetric_algos.index(curr_asym) if curr_asym in st.session_state.asymmetric_algos else 0,
                key="asymmetric_algo_input"
            )
            st.session_state.config_changed["asymmetric_algorithm"] = asymmetric_algo

        with col2:
            st.write("**Key Size Settings:**")

            # Dynamically filter key sizes based on current active asymmetric algorithm
            active_algo = asymmetric_algo
            algo_key_lengths = [str(kl["value"]) for kl in st.session_state.key_lengths if kl["algo_name"].upper() == active_algo.upper()]
            if not algo_key_lengths:
                algo_key_lengths = ["2048", "3072", "4096"] if active_algo.upper() == "RSA" else ["256", "384", "521"]

            curr_kl = config.get("key_length", "2048")
            if curr_kl not in algo_key_lengths:
                algo_key_lengths.append(curr_kl)
            algo_key_lengths = sorted(list(set(algo_key_lengths)), key=int)

            key_length = st.selectbox(
                "Default Key Length (bits)",
                algo_key_lengths,
                index=algo_key_lengths.index(curr_kl) if curr_kl in algo_key_lengths else 0,
                key="key_length_input"
            )
            st.session_state.config_changed["key_length"] = key_length

            curr_min_kl = config.get("min_key_length", "2048")
            if curr_min_kl not in algo_key_lengths:
                algo_key_lengths.append(curr_min_kl)
            algo_key_lengths = sorted(list(set(algo_key_lengths)), key=int)

            min_key_length = st.selectbox(
                "Minimum Key Length (bits)",
                algo_key_lengths,
                index=algo_key_lengths.index(curr_min_kl) if curr_min_kl in algo_key_lengths else 0,
                key="min_key_length_input"
            )
            st.session_state.config_changed["min_key_length"] = min_key_length

            st.info(
                "💡 Larger key lengths provide better security but may impact performance.",
                icon="ℹ️"
            )

    # ── TAB 3: Validity ──
    with tab3:
        st.subheader("Certificate Validity Configuration")

        col1, _, col2 = st.columns([1, 0.1, 1])

        with col1:
            st.write("**Validity Constraints:**")

            max_validity = st.number_input(
                "Maximum Certificate Validity (days)",
                min_value=1, max_value=9999,
                value=int(config.get("max_cert_validity_days", 3650)),
                step=1,
                key="max_validity_input"
            )
            st.session_state.config_changed["max_cert_validity_days"] = str(max_validity)

            st.markdown("""
            **Validity Guidelines:**
            - **Short-lived certificates** (90 days): Higher security, frequent renewal
            - **Standard validity** (365 days): Balance between security and convenience
            - **Long-lived certificates** (2-10 years): Less frequent renewal, lower security
            """)

        with col2:
            st.write("**Current Configuration:**")

            current_default = int(config.get("default_validity_days", 365))
            current_max = int(config.get("max_cert_validity_days", 3650))

            col_left, col_right = st.columns(2)
            with col_left:
                st.metric("Default Validity", f"{current_default} days")
            with col_right:
                st.metric("Maximum Allowed", f"{current_max} days")

            st.info(
                f"Default certificates will be valid for {current_default} days. "
                f"Maximum allowed validity is {current_max} days."
            )

    # ── TAB 4: Advanced ──
    with tab4:
        st.subheader("Advanced Configuration")

        st.markdown("**System Information:**")

        col1, col2 = st.columns(2)
        with col1:
            st.write("- **Config Version:** 1.0")
            st.write(f"- **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"- **Total Settings:** {len(config)}")

        with col2:
            st.write("- **System Status:** 🟢 Active")
            st.write("- **Configuration Mode:** Advanced")
            st.write("- **Audit Logging:** Enabled")

        st.divider()

        st.markdown("**Raw Configuration (JSON Format):**")

        current_config = {**config, **st.session_state.config_changed}
        config_json = json.dumps(current_config, indent=2)

        st.markdown(f"""
        <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
        <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{config_json}</pre>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Save / Reset ──
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            try:
                # Trigger single API call to reset in DB config
                api_client.reset_config_to_defaults()
                st.session_state.config_data = _load_config()
                st.session_state.config_changed = {}
                st.warning("⚠️ Configuration reset to default values.")
                st.rerun()
            except http_requests.ConnectionError:
                st.error("❌ Cannot connect to backend.")
            except http_requests.HTTPError as e:
                st.error(f"Error resetting config: {e}")

    with col2:
        if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
            if st.session_state.config_changed:
                try:
                    # Single batch API call to update all changed configs in one go
                    api_client.update_config(st.session_state.config_changed)
                    
                    # Apply changes to local session state config_data
                    for key, value in st.session_state.config_changed.items():
                        st.session_state.config_data[key] = value
                    
                    st.session_state.config_changed = {}
                    st.success(
                        f"Configuration saved successfully!\n\n"
                        f"**Updated Settings:**\n"
                        f"- Hash Algorithm: {st.session_state.config_data.get('hash_algorithm')}\n"
                        f"- Asymmetric Algorithm: {st.session_state.config_data.get('asymmetric_algorithm')}\n"
                        f"- Default Validity: {st.session_state.config_data.get('default_validity_days')} days\n"
                        f"- Key Length: {st.session_state.config_data.get('key_length')} bits\n"
                        f"- Saved At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        icon="✅"
                    )
                except http_requests.HTTPError as e:
                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                    st.error(f"❌ Failed to save configuration: {detail}")
                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend. Is the server running?")
            else:
                st.info("No changes to save.")

    st.divider()

    # Configuration Summary metrics
    st.subheader("📊 Configuration Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)
    effective = {**config, **st.session_state.config_changed}

    with summary_col1:
        st.metric("Hash Algorithm", effective.get("hash_algorithm", "N/A"))
    with summary_col2:
        st.metric("Asymmetric Algorithm", effective.get("asymmetric_algorithm", "N/A"))
    with summary_col3:
        st.metric("Default Validity", f"{effective.get('default_validity_days', 'N/A')} days")

    st.divider()
