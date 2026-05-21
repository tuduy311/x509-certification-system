import streamlit as st
from styles.dashboard import Dashboard_CSS


def user_dashboard():
    st.markdown(Dashboard_CSS, unsafe_allow_html = True)
    
    st.markdown(f"""<div class='admin-header'> 
                <div class='admin-title'>📋 User Dashboard </div>
                <div>
                <span style='font-size:22px'> Welcome back, <b>{st.session_state.username}</b>! </span> <span class='user-badge'>👤 {st.session_state.role.upper()}</span>\
                </div>
                </div>""", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["⚙️ Account & Keys", "📜 Certificates", "🔍 Search & CRL"])
    with tab1:
        st.subheader("Account & Key Management")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">🔑 Generate Key Pair</div>
                <div class="admin-content">Generate a new RSA or ECC public/private key pair for certificates.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Generate New Keys", use_container_width=True)
               
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📥 Import Key</div>
                <div class="admin-content">Import an existing public or private key for tracking.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Import Key", use_container_width=True)
                
        with col2:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">🔒 Change Password</div>
                <div class="admin-content">Update your account password for security.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Change Password", use_container_width=True)
               
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📊 My Keys</div>
                <div class="admin-content">View all your generated and imported key pairs.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("View All Keys", use_container_width=True)

    with tab2:
        st.subheader("Certificate Management")
    
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📝 Request Certificate</div>
                <div class="admin-content">Submit a Certificate Signing Request (CSR) for X.509 certificate issuance.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Request Certificate", use_container_width=True)
               
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">⬇️ Download Certificate</div>
                <div class="admin-content">Download your issued certificates (PEM, DER, PKCS12 formats).</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Download Certificate", use_container_width=True)
               
        with col2:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📋 My Certificates</div>
                <div class="admin-content">View all your certificate requests (pending & issued) and track their status.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("View My Certificates", use_container_width=True)
              
            
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">🚫 Revoke Certificate</div>
                <div class="admin-content">Request revocation of an issued certificate.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Revoke Certificate", use_container_width=True)

        st.markdown("---")
        st.subheader("Other Certificates")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📤 Upload Certificate</div>
                <div class="admin-content">Upload and track certificates from other sources for monitoring and verification.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Upload Certificate", use_container_width=True)

    with tab3:
        st.subheader("Certificate Search & Revocation List")
    
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">🔍 Search Certificate</div>
                <div class="admin-content">Search for certificates by domain, CN, serial number or issuer.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Search Certificates", use_container_width=True)
                
        with col2:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📋 View CRL</div>
                <div class="admin-content">View the Certificate Revocation List (CRL) of all revoked certificates in the system.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("View Revocation List", use_container_width=True)
                
    # User stats
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Certificates", 2)
    with col2:
        st.metric("Pending Requests", 1)
    with col3:
        st.metric("Revoked Certificates", 0)
    with col4:
        st.metric("Key Pairs", 3)
           
            