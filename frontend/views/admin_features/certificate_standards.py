import streamlit as st
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

# Mock Data Model
@dataclass
class SystemConfig:
    key: str
    value: str

# Mock Data Generator
def get_mock_config() -> Dict[str, str]:
    """Generate mock system configuration data"""
    return {
        "default_validity_days": "365",
        "asymmetric_algorithm": "RSA",
        "hash_algorithm": "SHA256",
        "key_length": "2048",
        "crl_update_days": "30",
        "max_cert_validity_days": "3650",
        "min_key_length": "2048",
        "enable_ecc": "true",
        "enable_rsa": "true",
        "certificate_version": "3",
    }

def certificate_standards():
    """Certificate Standards Configuration page"""
    
    # Initialize session state
    if "config_data" not in st.session_state:
        st.session_state.config_data = get_mock_config()
    if "config_changed" not in st.session_state:
        st.session_state.config_changed = {}
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Certificate Standards")
    st.markdown("Configure default certificate parameters and security settings")
    
    st.divider()
    
    # Get current config
    config = st.session_state.config_data
    
    # Tabs for different configuration sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "  Basic Settings",
        "  Encryption",
        "  Validity",
        "  Advanced"
    ])
    
    # __________________ TAB 1: Basic Settings __________________
    with tab1:
        st.subheader("Basic Certificate Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Default Settings:**")
            
            hash_algo = st.selectbox(
                "Default Hash Algorithm",
                ["SHA256", "SHA384", "SHA512"],
                index=0 if config.get("hash_algorithm") == "SHA256" else 
                      1 if config.get("hash_algorithm") == "SHA384" else 2,
                key="hash_algo_input"
            )
            st.session_state.config_changed["hash_algorithm"] = hash_algo
            
            cert_version = st.selectbox(
                "Certificate Version",
                ["1", "2", "3"],
                index=2 if config.get("certificate_version") == "3" else 0,
                key="cert_version_input"
            )
            st.session_state.config_changed["certificate_version"] = cert_version
        
        with col2:
            st.write("**Default Validity Period:**")
            
            default_validity = st.number_input(
                "Default Validity (days)",
                min_value=1,
                max_value=3650,
                value=int(config.get("default_validity_days", 365)),
                step=1,
                key="default_validity_input"
            )
            st.session_state.config_changed["default_validity_days"] = str(default_validity)
            
            crl_update = st.number_input(
                "CRL Update Interval (days)",
                min_value=1,
                max_value=365,
                value=int(config.get("crl_update_days", 30)),
                step=1,
                key="crl_update_input"
            )
            st.session_state.config_changed["crl_update_days"] = str(crl_update)
    
    # __________________ TAB 2: Encryption __________________
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
            
            asymmetric_algo = st.selectbox(
                "Default Asymmetric Algorithm",
                ["RSA", "ECC"],
                index=0 if config.get("asymmetric_algorithm") == "RSA" else 1,
                key="asymmetric_algo_input"
            )
            st.session_state.config_changed["asymmetric_algorithm"] = asymmetric_algo
        
        with col2:
            st.write("**Key Size Settings:**")
            
            key_length = st.selectbox(
                "Default Key Length (bits)",
                ["2048", "3072", "4096"],
                index=0 if config.get("key_length") == "2048" else 
                      1 if config.get("key_length") == "3072" else 2,
                key="key_length_input"
            )
            st.session_state.config_changed["key_length"] = key_length
            
            min_key_length = st.selectbox(
                "Minimum Key Length (bits)",
                ["2048", "3072", "4096"],
                index=0 if config.get("min_key_length") == "2048" else 
                      1 if config.get("min_key_length") == "3072" else 2,
                key="min_key_length_input"
            )
            st.session_state.config_changed["min_key_length"] = min_key_length
            
            st.info(
                "💡 Larger key lengths provide better security but may impact performance. "
                "Minimum key length should not exceed default key length.",
                icon="ℹ️"
            )
    
    # __________________ TAB 3: Validity __________________
    with tab3:
        st.subheader("Certificate Validity Configuration")
        
        col1, _, col2 = st.columns([1, 0.1, 1])
        
        with col1:
            st.write("**Validity Constraints:**")
            
            max_validity = st.number_input(
                "Maximum Certificate Validity (days)",
                min_value=1,
                max_value=9999,
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
                f"Maximum allowed validity is {current_max} days.",
            )
    
    # __________________ TAB 4: Advanced __________________
    with tab4:
        st.subheader("Advanced Configuration")
        
        st.markdown("**System Information:**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"- **Config Version:** 1.0")
            st.write(f"- **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"- **Total Settings:** {len(config)}")
        
        with col2:
            st.write(f"- **System Status:** 🟢 Active")
            st.write(f"- **Configuration Mode:** Advanced")
            st.write(f"- **Audit Logging:** Enabled")
        
        st.divider()
        
        st.markdown("**Raw Configuration (JSON Format):**")
        
        import json
        current_config = st.session_state.config_changed if st.session_state.config_changed else config
        config_json = json.dumps(current_config, indent=2)
        
        # Display with dark background and light text
        st.markdown(f"""
        <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
        <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{config_json}</pre>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    # Save Configuration
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.config_data = get_mock_config()
            st.session_state.config_changed = {}
            st.warning("⚠️ Configuration reset to default values.")
            st.rerun()
    
    with col2:
        if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
            # Update session state with new values
            st.session_state.config_data.update(st.session_state.config_changed)
            
            # Clear changed items
            st.session_state.config_changed = {}
            
            # Display success message
            st.success(
                f"✅ Configuration saved successfully!\n\n"
                f"**Updated Settings:**\n"
                f"- Hash Algorithm: {st.session_state.config_data.get('hash_algorithm')}\n"
                f"- Asymmetric Algorithm: {st.session_state.config_data.get('asymmetric_algorithm')}\n"
                f"- Default Validity: {st.session_state.config_data.get('default_validity_days')} days\n"
                f"- Key Length: {st.session_state.config_data.get('key_length')} bits\n"
                f"- Saved At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                icon="✅"
            )
            
            st.info(
                "📌 Changes have been applied. New certificates will use these settings.",
                icon="ℹ️"
            )
    
    with col3:
        pass  # Spacer

    st.divider()

    # Configuration Summary
    st.subheader(" Configuration Summary")
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.metric(
            "Hash Algorithm",
            st.session_state.config_changed.get("hash_algorithm", config.get("hash_algorithm"))
        )
    
    with summary_col2:
        st.metric(
            "Asymmetric Algorithm",
            st.session_state.config_changed.get("asymmetric_algorithm", config.get("asymmetric_algorithm"))
        )
    
    with summary_col3:
        st.metric(
            "Default Validity",
            f"{st.session_state.config_changed.get('default_validity_days', config.get('default_validity_days'))} days"
        )
    
    st.divider()
