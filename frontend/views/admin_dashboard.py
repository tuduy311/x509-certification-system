import streamlit as st

from styles.dashboard import Dashboard_CSS


def admin_dashboard():
    st.markdown(Dashboard_CSS, unsafe_allow_html = True)

    # st.markdown("<div class='admin-title'>🛡️ Admin Dashboard </div>", unsafe_allow_html= True);
    # st.markdown(f" Welcome, **{st.session_state.username}**! <span class='admin-badge'>⚙️ {st.session_state.role.upper()}</span>", unsafe_allow_html=True)
    st.markdown(f"""<div class='admin-header'> 
                <div class='admin-title'>🛡️ Admin Dashboard </div>
                <div>
                <span style='font-size:22px'> Welcome, <b>{st.session_state.username}</b>! </span> <span class='admin-badge'>⚙️ {st.session_state.role.upper()}</span>\
                </div>
                </div>""", unsafe_allow_html=True)
    st.markdown("---")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Management", "⚙️ System", "📋 Logs"])

    #__________________ tab1 ____________________
    with tab1:
        st.subheader("Management Certificate")
    
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="admin-card"> 
                <div class="admin-title"> ✅ Approve Certificate Requests </div>
                <div class="admin-content"> Approve pending certificate signing requests from users. </div>
            </div>
            """, unsafe_allow_html = True)
            st.button("View Requests", use_container_width=True)

            st.markdown("""
            <div class="admin-card"> 
                <div class="admin-title"> ❌ Reject Requests </div>
                <div class="admin-content"> Reject certificate signing requests with reason. </div>
            </div>
            """, unsafe_allow_html = True)
            st.button("Review & Reject", use_container_width=True)

            st.markdown("""
            <div class="admin-card"> 
                <div class="admin-title"> 🔄 Renew Certificates </div>
                <div class="admin-content"> Renew expiring certificates for users. </div>
            </div>
            """, unsafe_allow_html = True)
            st.button("Renew Certificate", use_container_width=True)

        with col2:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">🚫 Revoke Certificates</div>
                <div class="admin-content">Revoke active certificates immediately.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Manage Revocations", use_container_width=True)
            
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📋 Issued Certificates</div>
                <div class="admin-content">View and manage all issued certificates.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("View All Certificates", use_container_width=True)
            
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📨 Revocation Requests</div>
                <div class="admin-content">Review pending certificate revocation requests.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Review Requests", use_container_width=True)

        st.markdown("---")
        st.subheader("Certificate Revocation List (CRL)")
        st.markdown("""
        <div class="admin-card">
            <div class="admin-title">📝 Update CRL</div>
            <div class="admin-content">Generate and publish new Certificate Revocation List.</div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Update Revocation List", use_container_width=True)
    #__________________ tab2 ____________________
    with tab2:
        st.subheader("System Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title"> 🔑 Generate Root Key Pair </div>
                <div class ="admin-content"> Generate RSA/ECC root private and public key pair </div>
            </div>
            """, unsafe_allow_html = True)
            st.button("Generate Key Pair", use_container_width = True)

            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">📜 Generate Root Certificate</div>
                <div class="admin-content">Create self-signed root CA certificate.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Generate Certificate", use_container_width=True)
    
        with col2:
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">🔒 Change Admin Password</div>
                <div class="admin-content"> Update administrator account password. </div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Change Password", use_container_width=True)
              
            st.markdown("""
            <div class="admin-card">
                <div class="admin-title">⚙️ Certificate Standards</div>
                <div class="admin-content"> Configure default certificate parameters.</div>
            </div>
            """, unsafe_allow_html=True)
            st.button("Configure Standards", use_container_width=True)
                
        st.markdown("---")
        st.subheader("Default Security Configuration")
        
        algorithm = st.selectbox("Asymmetric Algorithm", ["RSA", "ECC"], key="asymmetric_algo")
        hash_algorithm = st.selectbox("Hash Algorithm", ["SHA256", "SHA384", "SHA512"], key="hash_algo")
        key_length = st.selectbox("Key Length", [2048, 3072, 4096], key="key_len")
        validity = st.selectbox("Default Certificate Validity", ["1 Year", "2 Years", "5 Years"], key="cert_validity")
        
        if st.button("💾 Save Configuration", use_container_width=True):
            st.success("✅ Configuration saved successfully!")

    #__________________ tab3 ____________________
    with tab3:
        st.subheader("System logs")

        st.markdown("""
        <div class="admin-card">
            <div class="admin-title">📊 Activity Monitoring</div>
            <div class="admin-content"> Monitor important system activities and security events.</div>
        </div>
        """, unsafe_allow_html=True)
    
        log_data = [
            {"Time": "2026-05-17 10:00", "User": "admin", "Action": "Generated Root Certificate"},
            {"Time": "2026-05-17 10:30", "User": "admin", "Action": "Approved Certificate Request"},
            {"Time": "2026-05-17 11:00", "User": "admin", "Action": "Revoked Certificate"}
        ]
        st.dataframe(log_data, use_container_width=True)
    
        st.markdown("""
        <div class="admin-card">
            <div class="admin-title">📥 Export Logs</div>
            <div class="admin-content">Download system logs for backup or audit purposes.</div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Export Logs", use_container_width=True)
            
    st.markdown("---")

    # Admin stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", 45)
    with col2:
        st.metric("Pending Requests", 7)
    with col3:
        st.metric("Active Certificates", 182)
    with col4:
        st.metric("System Health", "🟢 Good")