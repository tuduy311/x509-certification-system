import streamlit as st
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
from enum import Enum

# Enums
class KeyStatus(str, Enum):
    GENERATED = "GENERATED"
    IMPORTED = "IMPORTED"
    REVOKED = "REVOKED"
    ACTIVE = "ACTIVE"

class KeyAlgorithm(str, Enum):
    RSA = "RSA"
    ECDSA = "ECDSA"
    DSA = "DSA"

# Mock Data Model
@dataclass
class KeyPairOut:
    id: int
    algorithm: KeyAlgorithm
    key_size: int
    public_key_fingerprint: str
    created_at: datetime
    status: KeyStatus
    description: str

def get_mock_user_key_pairs() -> List[KeyPairOut]:
    """Generate mock key pairs for current user"""
    return [
        KeyPairOut(
            id=1,
            algorithm=KeyAlgorithm.RSA,
            key_size=2048,
            public_key_fingerprint="SHA256:aB1c2D3e4F5g6H7i8J9k0L1m2N3o4P5q6R7s8T9u",
            created_at=datetime.now() - timedelta(days=30),
            status=KeyStatus.ACTIVE,
            description="Main web server key"
        ),
        KeyPairOut(
            id=2,
            algorithm=KeyAlgorithm.ECDSA,
            key_size=256,
            public_key_fingerprint="SHA256:qP9o8N7m6L5k4J3i2H1g0F9e8D7c6B5a4Z3y2X1w",
            created_at=datetime.now() - timedelta(days=60),
            status=KeyStatus.ACTIVE,
            description="Secondary backup key"
        ),
        KeyPairOut(
            id=3,
            algorithm=KeyAlgorithm.RSA,
            key_size=4096,
            public_key_fingerprint="SHA256:wX1y2Z3a4B5c6D7e8F9g0H1i2J3k4L5m6N7o8P9q",
            created_at=datetime.now() - timedelta(days=120),
            status=KeyStatus.REVOKED,
            description="Old development key"
        ),
    ]

def generate_key_pair():
    
    # Initialize session state
    if "generated_keys" not in st.session_state:
        st.session_state.generated_keys = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Generate Key Pair")
    st.markdown("Generate a new public/private key pair for certificate signing requests")
    
    st.divider()
    
    # Create tabs
    tab1, tab2 = st.tabs([" Generate New Key", " My Key Pairs"])
    
    with tab1:
        st.subheader("Create New Key Pair")
        
        col1, col2 = st.columns(2)
        
        with col1:
            algorithm = st.selectbox(
                "Algorithm:",
                options=[algo.value for algo in KeyAlgorithm],
                key="key_algo"
            )
            
            key_size = st.number_input(
                "Key Size (bits):",
                min_value=2048,
                max_value=4096,
                value=2048,
                step=256,
                key="key_size"
            )
        
        with col2:
            password_protect = st.checkbox(
                "🔐 Password protect key",
                value=False,
                key="key_pwd_protect"
            )
            
            if password_protect:
                key_password = st.text_input(
                    "Key Password:",
                    type="password",
                    key="key_pwd"
                )
                confirm_password = st.text_input(
                    "Confirm Password:",
                    type="password",
                    key="key_pwd_confirm"
                )
        
        st.divider()
        
        # Key description
        st.markdown("**📝 Key Description:**")
        key_description = st.text_area(
            "Optional description for this key pair:",
            placeholder="e.g., Main web server key, Backup key, Development key",
            height=80,
            key="key_desc"
        )
        
        st.divider()
        
        # Security considerations
        with st.expander("🔒 Security Considerations"):
            st.markdown("""
            - **Key Size:** Larger keys (3072, 4096) provide better security but slower performance
            - **Algorithm:** RSA is widely supported; ECDSA is more modern and efficient
            - **Password Protection:** Protect private keys with strong passwords
            - **Backup:** Always backup your private keys in a secure location
            - **Rotation:** Regularly rotate keys and revoke old ones
            """)
        
        st.divider()
        
        # Generation summary
        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #4299e1; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #4299e1; margin-bottom: 10px;">🔐 Key Pair Summary</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0;"><strong>Algorithm:</strong> {algorithm}</div>
        <div style="margin: 5px 0;"><strong>Key Size:</strong> {key_size} bits</div>
        <div style="margin: 5px 0;"><strong>Protected:</strong> {'✅ Yes' if password_protect else '❌ No'}</div>
        <div style="margin: 5px 0;"><strong>Description:</strong> {key_description if key_description else 'Not specified'}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔨 Generate Key Pair", use_container_width=True, key="btn_generate_key"):
            if password_protect and key_password != confirm_password:
                st.error("❌ Passwords do not match!")
            elif password_protect and len(key_password) < 8:
                st.error("❌ Password must be at least 8 characters!")
            else:
                new_key = {
                    "id": len(st.session_state.generated_keys) + 1,
                    "algorithm": algorithm,
                    "key_size": key_size,
                    "protected": password_protect,
                    "description": key_description,
                    "timestamp": datetime.now()
                }
                st.session_state.generated_keys.append(new_key)
                
                with st.spinner("Generating key pair... (This may take a moment)"):
                    import time
                    time.sleep(2)
                
                st.success(f"""
                ✅ Key Pair Generated Successfully!
                
                **Key Details:**
                - **Key ID:** {new_key['id']}
                - **Algorithm:** {algorithm}
                - **Size:** {key_size} bits
                - **Protected:** {'Yes' if password_protect else 'No'}
                - **Generated:** {new_key['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                
                **⚠️ Important:**
                - Keep your private key secure and confidential
                - Download and backup your key pair
                - Use this key for your CSR requests
                """)
    
    with tab2:
        st.subheader("My Key Pairs")
        
        all_keys = get_mock_user_key_pairs()
        
        if not all_keys:
            st.info("No key pairs yet. Generate your first key pair to get started.")
        else:
            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Active", len([k for k in all_keys if k.status == KeyStatus.ACTIVE]))
            with col2:
                st.metric("🔄 Total", len(all_keys))
            with col3:
                st.metric("🚫 Revoked", len([k for k in all_keys if k.status == KeyStatus.REVOKED]))
            
            st.divider()
            
            # Display key pairs as expandable sections
            for key in all_keys:
                status_icon = "✅" if key.status == KeyStatus.ACTIVE else ("🔄" if key.status == KeyStatus.IMPORTED else "🚫")
                
                with st.expander(f"{status_icon} Key #{key.id} - {key.algorithm.value} ({key.key_size} bits) - {key.status.value}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Key ID:** {key.id}")
                        st.write(f"**Algorithm:** {key.algorithm.value}")
                        st.write(f"**Key Size:** {key.key_size} bits")
                        st.write(f"**Status:** {key.status.value}")
                    
                    with col2:
                        st.write(f"**Created:** {key.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Days Old:** {(datetime.now() - key.created_at).days} day(s)")
                        st.write(f"**Description:** {key.description}")
                    
                    st.divider()
                    
                    # Fingerprint
                    st.markdown("**🔐 Public Key Fingerprint:**")
                    st.markdown(f"""
                    <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
                    <pre style="margin: 0; word-break: break-all;">{key.public_key_fingerprint}</pre>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Actions
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📥 Download", key=f"download_key_{key.id}"):
                            st.success(f"Key pair #{key.id} download started")
                    
                    with col2:
                        if st.button("📋 Copy Fingerprint", key=f"copy_key_{key.id}"):
                            st.success("Fingerprint copied to clipboard!")
                    
                    with col3:
                        if key.status == KeyStatus.ACTIVE and st.button("🚫 Revoke", key=f"revoke_key_{key.id}"):
                            st.warning(f"Key #{key.id} revoked")
