import streamlit as st
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# Enums
class CertStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# Mock Data Model
@dataclass
class RevocationRequestOut:
    id: int
    certificate_id: int
    user_id: int
    reason: str
    status: CertStatus
    created_at: datetime
    certificate_subject: str
    certificate_serial: str

# Mock Data Generator
def get_mock_revocation_requests() -> List[RevocationRequestOut]:
    """Generate mock revocation request data"""
    return [
        RevocationRequestOut(
            id=1,
            certificate_id=5,
            user_id=10,
            reason="Key Compromise",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(days=2),
            certificate_subject="CN=user1@example.com,O=Organization,C=US",
            certificate_serial="05:E6:F7:08:09:0A:0B:0C"
        ),
        RevocationRequestOut(
            id=2,
            certificate_id=12,
            user_id=15,
            reason="Superseded",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(days=1),
            certificate_subject="CN=user2@example.com,O=Organization,C=US",
            certificate_serial="0C:D5:E6:F7:08:09:0A:0B"
        ),
        RevocationRequestOut(
            id=3,
            certificate_id=8,
            user_id=12,
            reason="Cessation of Operation",
            status=CertStatus.PENDING,
            created_at=datetime.now() - timedelta(hours=6),
            certificate_subject="CN=service@example.com,O=Organization,C=US",
            certificate_serial="08:B4:C5:D6:E7:F8:09:0A"
        ),
        RevocationRequestOut(
            id=4,
            certificate_id=3,
            user_id=8,
            reason="CA Compromise",
            status=CertStatus.APPROVED,
            created_at=datetime.now() - timedelta(days=5),
            certificate_subject="CN=old-admin@example.com,O=Organization,C=US",
            certificate_serial="03:C4:D5:E6:F7:08:09:0A"
        ),
        RevocationRequestOut(
            id=5,
            certificate_id=7,
            user_id=11,
            reason="Affiliation Changed",
            status=CertStatus.REJECTED,
            created_at=datetime.now() - timedelta(days=7),
            certificate_subject="CN=user3@example.com,O=OldOrg,C=US",
            certificate_serial="07:A3:B4:C5:D6:E7:F8:09"
        ),
    ]

def revocation_requests():
    
    # Initialize session state
    if "revocation_decisions" not in st.session_state:
        st.session_state.revocation_decisions = []
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(" Certificate Revocation Requests")
    st.markdown("Review and process pending certificate revocation requests from users")
    
    st.divider()
    
    # Get mock data
    all_requests = get_mock_revocation_requests()
    
    # Filter PENDING requests only
    pending_requests = [req for req in all_requests if req.status == CertStatus.PENDING]
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏳ Pending", len(pending_requests))
    with col2:
        st.metric("✅ Approved", len([r for r in all_requests if r.status == CertStatus.APPROVED]))
    with col3:
        st.metric("❌ Rejected", len([r for r in all_requests if r.status == CertStatus.REJECTED]))
    with col4:
        st.metric("📊 Total", len(all_requests))
    
    st.divider()
    
    # Create tabs
    tab1, tab2 = st.tabs([" Pending Requests", " All Requests"])
    
    with tab1:
        st.subheader("Pending Revocation Requests")
        
        # Check if there are pending requests
        if not pending_requests:
            st.info("✅ No pending revocation requests.")
        else:
            # Pending requests table
            pending_data = []
            for req in pending_requests:
                pending_data.append({
                    "Request ID": req.id,
                    "Certificate ID": req.certificate_id,
                    "User ID": req.user_id,
                    "Subject": req.certificate_subject,
                    "Reason": req.reason,
                    "Requested": req.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            df_pending = pd.DataFrame(pending_data)
            st.dataframe(
                df_pending,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Request ID": st.column_config.NumberColumn(width="small"),
                    "Certificate ID": st.column_config.NumberColumn(width="small"),
                    "User ID": st.column_config.NumberColumn(width="small"),
                    "Subject": st.column_config.TextColumn(width="large"),
                    "Reason": st.column_config.TextColumn(width="medium"),
                    "Requested": st.column_config.TextColumn(width="medium")
                }
            )
            
            st.divider()
            
            # Request Selection
            st.subheader(" Review Request")
            
            request_options = [
                f"Request #{req.id} - Cert #{req.certificate_id} - {req.reason}"
                for req in pending_requests
            ]
            
            selected_idx = st.selectbox(
                "Select a revocation request to review:",
                range(len(pending_requests)),
                format_func=lambda i: request_options[i],
                key="pending_revocation_select"
            )
            
            selected_request = pending_requests[selected_idx]
            
            st.divider()
            
            # Request Details
            st.subheader(" Request Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Request ID:** {selected_request.id}")
                st.write(f"**Certificate ID:** {selected_request.certificate_id}")
                st.write(f"**User ID:** {selected_request.user_id}")
                st.write(f"**Status:** {selected_request.status.value}")
            
            with col2:
                st.write(f"**Subject:** `{selected_request.certificate_subject}`")
                st.write(f"**Serial Number:** `{selected_request.certificate_serial}`")
                st.write(f"**Requested:** {selected_request.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Days Pending:** {(datetime.now() - selected_request.created_at).days} day(s)")
            
            st.divider()
            
            # Revocation Reason
            st.markdown("**Revocation Reason:**")
            st.markdown(f"""
            <div style="background-color: #2d3748; border-left: 4px solid #ed8936; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="color: #e0e0e0; font-size: 15px;">{selected_request.reason}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Verification Section
            st.markdown("**✓ Verification Checklist:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                verify_identity = st.checkbox(
                    "User identity verified",
                    key=f"verify_identity_{selected_request.id}"
                )
            
            with col2:
                verify_reason = st.checkbox(
                    "Revocation reason is valid",
                    key=f"verify_reason_{selected_request.id}"
                )
            
            # Additional comments
            admin_notes = st.text_area(
                "Additional Notes (optional):",
                placeholder="Add any relevant notes about this revocation request...",
                key=f"admin_notes_{selected_request.id}"
            )
            
           
            # Decision Summary
            st.markdown("""
            <div style="background-color: #2d3748; border-left: 4px solid #48bb78; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="font-weight: bold; color: #48bb78; margin-bottom: 10px;">✓ Decision Summary</div>
            <div style="color: #e0e0e0; font-size: 14px;">
            <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">{'✅' if verify_identity else '⏳'}</span> User verified: {'Yes' if verify_identity else 'No'}</div>
            <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">{'✅' if verify_reason else '⏳'}</span> Reason valid: {'Yes' if verify_reason else 'No'}</div>
            <div style="margin: 5px 0; display: flex; align-items: center;"><span style="margin-right: 8px;">📝</span> Notes: {'Added' if admin_notes else 'None'}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(
                    "✅ Approve Revocation",
                    disabled=not (verify_identity and verify_reason),
                    key=f"approve_revoke_{selected_request.id}",
                    use_container_width=True
                ):
                    st.session_state.revocation_decisions.append({
                        "request_id": selected_request.id,
                        "decision": "APPROVED",
                        "timestamp": datetime.now()
                    })
                    
                    st.success(f"""
                    ✅ Revocation Request #{selected_request.id} Approved!
                    
                    **Details:**
                    - Certificate ID: {selected_request.certificate_id}
                    - Revocation Reason: {selected_request.reason}
                    - Approved At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    
                    Certificate will be revoked immediately and CRL updated.
                    """)
            
            with col2:
                if st.button(
                    "❌ Reject Request",
                    key=f"reject_revoke_{selected_request.id}",
                    use_container_width=True
                ):
                    reject_reason = st.text_input(
                        "Reason for rejection:",
                        key=f"reject_reason_{selected_request.id}"
                    )
                    
                    if reject_reason:
                        st.session_state.revocation_decisions.append({
                            "request_id": selected_request.id,
                            "decision": "REJECTED",
                            "reason": reject_reason,
                            "timestamp": datetime.now()
                        })
                        
                        st.error(f"""
                        ❌ Revocation Request #{selected_request.id} Rejected!
                        
                        **Rejection Reason:** {reject_reason}
                        - Certificate ID: {selected_request.certificate_id}
                        - Rejected At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        
                        User will be notified of the rejection.
                        """)
    
    with tab2:
        st.subheader("All Revocation Requests")
        
        # All requests table
        all_data = []
        for req in all_requests:
            all_data.append({
                "ID": req.id,
                "Certificate ID": req.certificate_id,
                "User ID": req.user_id,
                "Subject": req.certificate_subject,
                "Reason": req.reason,
                "Status": req.status.value,
                "Requested": req.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        df_all = pd.DataFrame(all_data)
        
        # Filter by status
        status_filter = st.multiselect(
            "Filter by Status:",
            options=[CertStatus.PENDING.value, CertStatus.APPROVED.value, CertStatus.REJECTED.value],
            default=[CertStatus.PENDING.value, CertStatus.APPROVED.value, CertStatus.REJECTED.value],
            key="all_revocation_status_filter"
        )
        
        if status_filter:
            df_all = df_all[df_all["Status"].isin(status_filter)]
        
        st.dataframe(
            df_all,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn(width="small"),
                "Certificate ID": st.column_config.NumberColumn(width="small"),
                "User ID": st.column_config.NumberColumn(width="small"),
                "Subject": st.column_config.TextColumn(width="large"),
                "Reason": st.column_config.TextColumn(width="medium"),
                "Status": st.column_config.TextColumn(width="medium"),
                "Requested": st.column_config.TextColumn(width="medium")
            }
        )
        
        st.info(f"📊 Showing {len(df_all)} of {len(all_requests)} requests")
