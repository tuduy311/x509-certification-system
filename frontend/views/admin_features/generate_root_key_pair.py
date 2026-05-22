import streamlit as st
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List

# Enums
class KeyStatus(str, Enum):
    GENERATED = "GENERATED"
    PENDING = "PENDING"
    ARCHIVED = "ARCHIVED"

class KeyAlgorithm(str, Enum):
    RSA = "RSA"
    ECDSA = "ECDSA"

# Mock Data Model
@dataclass
class RootKeyPairOut:
    id: int
    algorithm: KeyAlgorithm
    key_size: int
    public_key_fingerprint: str
    created_at: datetime
    status: KeyStatus
    description: str

# Mock Data Generator
def get_mock_key_pairs() -> List[RootKeyPairOut]:
    """Generate mock root key pair records"""
    return [
        RootKeyPairOut(
            id=1,
            algorithm=KeyAlgorithm.RSA,
            key_size=2048,
            public_key_fingerprint="SHA256:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            created_at=datetime(2026, 1, 15, 10, 30),
            status=KeyStatus.GENERATED,
            description="Initial Root Key Pair for CA Setup"
        ),
        RootKeyPairOut(
            id=2,
            algorithm=KeyAlgorithm.RSA,
            key_size=4096,
            public_key_fingerprint="SHA256:b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7",
            created_at=datetime(2026, 1, 10, 14, 15),
            status=KeyStatus.ARCHIVED,
            description="Backup Root Key Pair"
        ),
        RootKeyPairOut(
            id=3,
            algorithm=KeyAlgorithm.ECDSA,
            key_size=256,
            public_key_fingerprint="SHA256:c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8",
            created_at=datetime(2025, 12, 20, 9, 0),
            status=KeyStatus.ARCHIVED,
            description="ECDSA Test Key Pair"
        ),
    ]

def generate_root_key_pair():
    
    # Initialize session state
    if "generated_key_pairs" not in st.session_state:
        st.session_state.generated_key_pairs = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Generate Root Key Pair")
    st.markdown("Create a new Root Key Pair for the Certificate Authority")
    
    st.divider()
    
    # Get mock data
    all_key_pairs = get_mock_key_pairs()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Generated", len([k for k in all_key_pairs if k.status == KeyStatus.GENERATED]))
    with col2:
        st.metric("📦 Total", len(all_key_pairs))
    with col3:
        st.metric("🔐 RSA Keys", len([k for k in all_key_pairs if k.algorithm == KeyAlgorithm.RSA]))
    with col4:
        st.metric("📊 ECDSA Keys", len([k for k in all_key_pairs if k.algorithm == KeyAlgorithm.ECDSA]))
    
    st.divider()
    
    # Create two tabs: Generate New & View Existing
    tab1, tab2 = st.tabs([" Generate New", " View Existing"])
    
    with tab1:
        st.subheader("Generate New Root Key Pair")
        st.markdown("Configure parameters for the new root key pair")
        
        col1, col2 = st.columns(2)
        
        with col1:
            algorithm = st.radio(
                "Select Key Algorithm:",
                options=["RSA", "ECDSA"],
                key="root_key_algo"
            )
            
            if algorithm == "RSA":
                key_size = st.selectbox(
                    "Key Size (bits):",
                    options=[2048, 3072, 4096],
                    index=0,
                    key="rsa_key_size"
                )
            else:  # ECDSA
                key_size = st.selectbox(
                    "Curve Size (bits):",
                    options=[256, 384, 521],
                    index=0,
                    key="ecdsa_key_size"
                )
        
        with col2:
            password_protection = st.checkbox(
                "🔒 Password Protect Key",
                value=True,
                key="root_key_password"
            )
            
            if password_protection:
                key_password = st.text_input(
                    "Key Password:",
                    type="password",
                    key="root_key_password_input"
                )
            
            # Additional options
            description = st.text_area(
                "Key Pair Description:",
                placeholder="e.g., Primary Root Key Pair for Production CA",
                key="root_key_description"
            )
        
      
        # Confirmation and Generate
        st.markdown("""
        <div style="background-color: #2d3748; border-left: 4px solid #4299e1; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #4299e1; margin-bottom: 10px;">⚙️ Configuration Summary</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0;"><strong>Algorithm:</strong> {algorithm}</div>
        <div style="margin: 5px 0;"><strong>Key Size:</strong> {key_size} bits</div>
        <div style="margin: 5px 0;"><strong>Password Protected:</strong> {'🔒 Yes' if password_protection else '🔓 No'}</div>
        <div style="margin: 5px 0;"><strong>Description:</strong> {description if description else 'No description'}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        confirm_generate = st.checkbox(
            "Confirm key pair generation",
            key="confirm_root_key_generate"
        )
        
        if st.button(
            "🔐 Generate Key Pair",
            disabled=not confirm_generate,
            key="btn_generate_root_key",
            use_container_width=True
        ):
            # Simulate generation
            with st.spinner("Generating root key pair..."):
                import time
                time.sleep(2)
                
                # Store in session
                new_key = {
                    "id": len(st.session_state.generated_key_pairs) + 1,
                    "algorithm": algorithm,
                    "key_size": key_size,
                    "fingerprint": f"SHA256:{''.join([hex(i)[2:] for i in range(32)])[:64]}",
                    "timestamp": datetime.now(),
                    "description": description,
                    "password_protected": password_protection
                }
                st.session_state.generated_key_pairs.append(new_key)
                
                st.success(f"""
                ✅ Root Key Pair Generated Successfully!
                
                - **Algorithm:** {algorithm}
                - **Key Size:** {key_size} bits
                - **Fingerprint:** {new_key['fingerprint']}
                - **Generated At:** {new_key['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                
                **⚠️ Important:** Download and securely store your private key immediately.
                The private key will not be shown again for security reasons.
                """)
        
        # Security Considerations (moved to end)
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
        st.subheader("Existing Root Key Pairs")
        
        if not all_key_pairs:
            st.info("No root key pairs found.")
        else:
            # Display as expandable sections
            for key_pair in all_key_pairs:
                status_color = "🟢" if key_pair.status == KeyStatus.GENERATED else "🔴"
                with st.expander(f"{status_color} {key_pair.algorithm.value} {key_pair.key_size}b - {key_pair.description}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {key_pair.id}")
                        st.write(f"**Algorithm:** {key_pair.algorithm.value}")
                        st.write(f"**Key Size:** {key_pair.key_size} bits")
                        st.write(f"**Status:** {key_pair.status.value}")
                    
                    with col2:
                        st.write(f"**Created:** {key_pair.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Fingerprint:** `{key_pair.public_key_fingerprint}`")
                        st.write(f"**Days Old:** {(datetime.now() - key_pair.created_at).days} day(s)")
                    
                    # Public Key Preview
                    st.markdown("**📄 Public Key:**")
                    public_key_sample = f"""-----BEGIN PUBLIC KEY-----
                    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA{key_pair.public_key_fingerprint[:32]}
                    {key_pair.public_key_fingerprint[32:64]}
                    -----END PUBLIC KEY-----"""
                    st.markdown(f"""
                    <div style="background-color: #1a1a1a; color: #e0e0e0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto;">
                    <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{public_key_sample}</pre>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Actions
                    action_col1, action_col2, action_col3 = st.columns(3)
                    
                    with action_col1:
                        if st.button(
                            "📥 Download",
                            key=f"download_key_{key_pair.id}"
                        ):
                            st.info(f"Download key pair {key_pair.id} - Feature would trigger actual download")
                    
                    with action_col2:
                        if st.button(
                            "📋 Copy Fingerprint",
                            key=f"copy_fingerprint_{key_pair.id}"
                        ):
                            st.success("Fingerprint copied to clipboard!")
                    
                    with action_col3:
                        if key_pair.status == KeyStatus.GENERATED and st.button(
                            "🗂️ Archive",
                            key=f"archive_key_{key_pair.id}"
                        ):
                            st.info(f"Key pair {key_pair.id} archived")
            
            st.divider()
            st.markdown("**Legend:** 🟢 Generated | 🔴 Archived")
