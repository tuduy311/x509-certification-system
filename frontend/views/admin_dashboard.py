import streamlit as st

Admin_Dashboard_CSS = """
<style>
    .admin-header {
        display: flex;
        justify-content: space-between;
        align-items:center;
        padding:15px 20px;
        border-radius:16px;
        background:rgba(255,255,255,0.1);
        margin-bottom:0;
    }

    .admin-header span {
        color: #FFFFFF !important;
    }

    .admin-header div {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff !important;
    }

    .admin-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        color: #fca5a5;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }

    /* container của toàn bộ tab */
    div[data-baseweb="tab-list"] {
        justify-content: center !important;
        gap: 15px;
    }
    
    /* Tab button */
    button[data-baseweb="tab"] {
        padding: 0 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.1) !important;
    }

    /* TEXT trong tab */
    button[data-baseweb="tab"] * {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #CBD5E1 !important;
    }

    /* Tab đang active */
    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(59,130,246,0.2);
        border-radius: 10px;

        transform: scale(1.1);  
        padding: 18px 18px !important;
    }

    /* Select box */
    div[data-baseweb="select"] > div {
        border: 1px solid #334155;
        min-height: 45px;
        background-color: rgba(255, 255, 255, 0.9) !important;
    }

    /* Option */
    li[role="option"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
    }

    /* Text bên trong option */
    li[role="option"] * {
        color: black !important;
    }

    /* Hover option */
    li[role="option"]:hover {
        background-color: #d2d3db;
    }
    
    div[data-baseweb="select"] * {
        color: black !important;
    }
    
    /* subheader */
    h3, h3 * {
        color: rgb(93, 203, 239, 0.5) !important;
    }

    .admin-card {
        background: rgba(30, 41, 59, 0.5) !important;
       # background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 20%, rgba(220, 38, 38, 0.05) 100%);
        border: 1px solid;
       # border-color: rgba(239, 68, 68, 0.2);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 10px;
    }

    .admin-title {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff !important;
    }

    [data-testid="column"] .stButton > button {
        margin-bottom: 24px !important;
    }

    .admin-content {
        font-size: 16px;
        color: #cbd5e1;
        line-height: 2;
    }
   
</style>
"""


def admin_dashboard():
    st.markdown(Admin_Dashboard_CSS, unsafe_allow_html = True)

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