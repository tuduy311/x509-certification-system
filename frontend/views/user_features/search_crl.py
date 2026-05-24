import streamlit as st
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
import pandas as pd

@dataclass
class RevokedCertificate:
    serial_number: str
    subject: str
    issuer: str
    revocation_date: datetime
    reason: str
    valid_to: datetime

def get_mock_crl_list() -> List[RevokedCertificate]:
    """Generate mock CRL (Certificate Revocation List)"""
    return [
        RevokedCertificate(
            serial_number="01:A2:B3:C4:D5:E6:F7:08",
            subject="CN=example1.com,O=Example Corp,C=US",
            issuer="CN=Root CA,O=Example Corp,C=US",
            revocation_date=datetime.now() - timedelta(days=15),
            reason="Key Compromise",
            valid_to=datetime.now() + timedelta(days=100)
        ),
        RevokedCertificate(
            serial_number="02:B3:C4:D5:E6:F7:08:09",
            subject="CN=example2.com,O=Example Corp,C=US",
            issuer="CN=Root CA,O=Example Corp,C=US",
            revocation_date=datetime.now() - timedelta(days=30),
            reason="Superseded",
            valid_to=datetime.now() - timedelta(days=50)
        ),
        RevokedCertificate(
            serial_number="03:C4:D5:E6:F7:08:09:0A",
            subject="CN=test.example.com,O=Example Corp,C=US",
            issuer="CN=Root CA,O=Example Corp,C=US",
            revocation_date=datetime.now() - timedelta(days=45),
            reason="Cessation of Operation",
            valid_to=datetime.now() + timedelta(days=200)
        ),
        RevokedCertificate(
            serial_number="04:D5:E6:F7:08:09:0A:0B",
            subject="CN=old.example.com,O=Example Corp,C=US",
            issuer="CN=Root CA,O=Example Corp,C=US",
            revocation_date=datetime.now() - timedelta(days=60),
            reason="Affiliation Changed",
            valid_to=datetime.now() - timedelta(days=20)
        ),
        RevokedCertificate(
            serial_number="05:E6:F7:08:09:0A:0B:0C",
            subject="CN=backup.example.com,O=Example Corp,C=US",
            issuer="CN=Root CA,O=Example Corp,C=US",
            revocation_date=datetime.now() - timedelta(days=5),
            reason="Privilege Withdrawn",
            valid_to=datetime.now() + timedelta(days=300)
        ),
    ]

def search_crl():
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Certificate Revocation List (CRL)")
    st.markdown("Search and view all revoked certificates in the system")
    
    st.divider()
    
    # Create tabs
    tab1, tab2 = st.tabs([" Search CRL", " CRL Statistics"])
    
    with tab1:
        st.subheader("Search Revoked Certificates")
        
        # Get CRL data
        crl_list = get_mock_crl_list()
        
        # Search options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_type = st.selectbox(
                "Search by:",
                ["Serial Number", "Subject (CN)", "Revocation Reason"],
                key="search_type"
            )
        
        with col2:
            search_query = st.text_input(
                "Search query:",
                placeholder="Enter search term...",
                key="search_query"
            )
        
        with col3:
            date_range = st.selectbox(
                "Revocation date range:",
                ["All", "Last 30 days", "Last 90 days", "Last 1 year"],
                key="date_range"
            )
        
        st.divider()
        
        # Filter CRL data based on search
        filtered_crl = crl_list
        
        if search_query:
            if search_type == "Serial Number":
                filtered_crl = [c for c in filtered_crl if search_query.lower() in c.serial_number.lower()]
            elif search_type == "Subject (CN)":
                filtered_crl = [c for c in filtered_crl if search_query.lower() in c.subject.lower()]
            elif search_type == "Revocation Reason":
                filtered_crl = [c for c in filtered_crl if search_query.lower() in c.reason.lower()]
        
        # Filter by date range
        now = datetime.now()
        if date_range == "Last 30 days":
            filtered_crl = [c for c in filtered_crl if (now - c.revocation_date).days <= 30]
        elif date_range == "Last 90 days":
            filtered_crl = [c for c in filtered_crl if (now - c.revocation_date).days <= 90]
        elif date_range == "Last 1 year":
            filtered_crl = [c for c in filtered_crl if (now - c.revocation_date).days <= 365]
        
        # Display results
        st.markdown(f"**📊 Found {len(filtered_crl)} revoked certificate(s)**")
        
        if not filtered_crl:
            st.info("No revoked certificates found matching your search criteria.")
        else:
            # Display as table
            crl_data = []
            for cert in filtered_crl:
                crl_data.append({
                    "Serial Number": cert.serial_number,
                    "Subject (CN)": cert.subject.split(",")[0].replace("CN=", ""),
                    "Revocation Date": cert.revocation_date.strftime('%Y-%m-%d'),
                    "Reason": cert.reason,
                    "Status": "🔴 Revoked"
                })
            
            df = pd.DataFrame(crl_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Serial Number": st.column_config.TextColumn(width="large"),
                    "Subject (CN)": st.column_config.TextColumn(width="large"),
                    "Revocation Date": st.column_config.TextColumn(width="medium"),
                    "Reason": st.column_config.TextColumn(width="large"),
                    "Status": st.column_config.TextColumn(width="small")
                }
            )
            
            st.divider()
            
            # Detailed view
            st.markdown("**📄 Detailed Information**")
            
            selected_idx = st.selectbox(
                "Select a certificate for details:",
                range(len(filtered_crl)),
                format_func=lambda i: f"Serial: {filtered_crl[i].serial_number}",
                key="crl_detail_select"
            )
            
            selected_cert = filtered_crl[selected_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Serial Number:** `{selected_cert.serial_number}`")
                st.write(f"**Subject:** `{selected_cert.subject}`")
                st.write(f"**Issuer:** `{selected_cert.issuer}`")
            
            with col2:
                st.write(f"**Revocation Date:** {selected_cert.revocation_date.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Revocation Reason:** {selected_cert.reason}")
                days_since = (datetime.now() - selected_cert.revocation_date).days
                st.write(f"**Revoked for:** {days_since} day(s)")
    
    with tab2:
        st.subheader("CRL Statistics & Information")
        
        crl_list = get_mock_crl_list()
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Revoked", len(crl_list))
        
        with col2:
            last_30 = len([c for c in crl_list if (datetime.now() - c.revocation_date).days <= 30])
            st.metric("📅 Last 30 Days", last_30)
        
        with col3:
            st.metric("🔑 Total Certificates", "2,450", delta="-12")
        
        with col4:
            revocation_rate = (len(crl_list) / 2450 * 100)
            st.metric("📊 Revocation Rate", f"{revocation_rate:.2f}%")
        
        st.divider()
        
        # Revocation reasons breakdown
        st.markdown("**📊 Revocation Reasons Breakdown**")
        
        reason_counts = {}
        for cert in crl_list:
            reason_counts[cert.reason] = reason_counts.get(cert.reason, 0) + 1
        
        reason_df = pd.DataFrame([
            {"Reason": reason, "Count": count}
            for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
        ])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(
                reason_df,
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.bar_chart(reason_df.set_index("Reason"))
        
        st.divider()
        
        # CRL Information
        st.markdown("**ℹ️ CRL Information**")
        
        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #4299e1; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0;"><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        <div style="margin: 5px 0;"><strong>Update Frequency:</strong> Daily at 00:00 UTC</div>
        <div style="margin: 5px 0;"><strong>Distribution Points:</strong> crl.example.com/root.crl</div>
        <div style="margin: 5px 0;"><strong>Format:</strong> DER/PEM</div>
        <div style="margin: 5px 0;"><strong>Signature Algorithm:</strong> SHA-256 with RSA</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Download CRL
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download CRL (DER)", use_container_width=True):
                st.success("CRL file download started (DER format)")
        
        with col2:
            if st.button("📥 Download CRL (PEM)", use_container_width=True):
                st.success("CRL file download started (PEM format)")
