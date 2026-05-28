import streamlit as st
from styles.dashboard import Dashboard_CSS

def user_dashboard():
    st.markdown(Dashboard_CSS, unsafe_allow_html = True)
    
    st.divider()
    
    st.markdown(f"""<div class='admin-header'> 
                <div class='admin-title'>📋 User Dashboard </div>
                <div>
                <span style='font-size:22px'> Welcome back, <b>{st.session_state.username}</b>! </span> <span class='user-badge'>👤 {st.session_state.role.upper()}</span>\
                </div>
                </div>""", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["⚙️ Settings & Keys", "📜 Certificates", "🔍 CRL"])
    
    with tab1:
        st.subheader("Settings & Key Management")

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">🔒 Change Password</div>
                <div class="admin-content">Update your account password for security.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Change Password", use_container_width=True):
                st.session_state.current_feature = "profile"
                st.rerun()

        with col2:   
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">🔑 Generate Key Pair</div>
                <div class="admin-content">Generate RSA or ECDSA key pairs for certificate signing requests.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Generate Keys", use_container_width=True):
                st.session_state.current_feature = "generate_key_pair"
                st.rerun()

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
            if st.button("Request Certificate", use_container_width=True):
                st.session_state.current_feature = "request_certificate"
                st.rerun()
               
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">⬇️ Download Certificate</div>
                <div class="admin-content">Download your issued certificates (PEM, DER, PKCS12 formats).</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Download Certificate", use_container_width=True):
                st.session_state.current_feature = "my_certificates"
                st.rerun()
               
        with col2:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📋 My Certificates</div>
                <div class="admin-content">View all your certificate requests (pending & issued) and track their status.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View My Certificates", use_container_width=True):
                st.session_state.current_feature = "my_certificates"
                st.rerun()
              
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">🚫 Revoke Certificate</div>
                <div class="admin-content">Request revocation of an issued certificate.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Revoke Certificate", use_container_width=True):
                st.session_state.current_feature = "revoke_certificate"
                st.rerun()

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
            if st.button("Upload Certificate", use_container_width=True):
                st.session_state.current_feature = "upload_certificate"
                st.rerun()

    with tab3:
        st.subheader("Revocation List")
    
        col1, col2 = st.columns(2)
                
        with col1:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📋 View CRL</div>
                <div class="admin-content">View the Certificate Revocation List (CRL) of all revoked certificates in the system.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Revocation List", use_container_width=True, key="btn_crl_dash"):
                st.session_state.current_feature = "search_crl"
                st.rerun()
           
            