import streamlit as st
from datetime import datetime
import api_client
import requests as http_requests


REVOCATION_REASONS = [
    "Key Compromise",
    "Affiliation Changed",
    "Superseded",
    "Cessation of Operation",
    "Certificate Hold",
    "Remove from CRL",
    "Privilege Withdrawn",
    "AA Compromise"
]


def revoke_certificate():

    # Initialize session state
    if "revoked_certs" not in st.session_state:
        st.session_state.revoked_certs = []

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("🚫 Request Certificate Revocation")
    st.markdown("Request to revoke one of your certificates")
    st.divider()

    tab1, tab2 = st.tabs(["🚫 Request Revocation", "📋 Revocation History"])

    with tab1:
        st.subheader("Create Revocation Request")

        # ── Fetch user's active certificates ──
        try:
            all_certificates = api_client.get_my_certificates()
        except http_requests.ConnectionError:
            st.error("❌ Cannot connect to backend.")
            return
        except http_requests.HTTPError as e:
            st.error(f"Backend error: {e}")
            return

        active_certs = [c for c in all_certificates if c["status"] == "approved"]

        if not active_certs:
            st.warning("⚠️ You have no active certificates available to revoke.")
        else:
            cert_options = [
                f"Cert #{c['id']} - {c['serial_number']} (Valid to: {str(c['valid_to'])[:10]})"
                for c in active_certs
            ]
            selected_idx = st.selectbox(
                "Select Certificate to Revoke:",
                range(len(active_certs)),
                format_func=lambda i: cert_options[i],
                key="cert_to_revoke"
            )

            selected_cert = active_certs[selected_idx]

            st.divider()

            st.markdown("**📄 Certificate Details:**")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**ID:** {selected_cert['id']}")
                st.write(f"**Serial Number:** `{selected_cert['serial_number']}`")

            with col2:
                st.write(f"**Valid From:** {str(selected_cert['valid_from'])[:10]}")
                st.write(f"**Valid To:** {str(selected_cert['valid_to'])[:10]}")
                try:
                    valid_to = datetime.fromisoformat(str(selected_cert["valid_to"]).replace("T", " ").split(".")[0])
                    days_left = (valid_to - datetime.utcnow()).days
                    st.write(f"**Expires In:** {days_left} days")
                except Exception:
                    pass

            st.divider()

            st.markdown("**🔍 Revocation Reason:**")

            reason = st.selectbox(
                "Select reason for revocation:",
                options=REVOCATION_REASONS,
                key="revoke_reason"
            )

            additional_notes = st.text_area(
                "Additional Notes (optional):",
                placeholder="Provide any additional details about the revocation request...",
                height=100,
                key="revoke_notes"
            )

            st.divider()

            # Warning
            st.markdown(f"""
            <div style="background-color: #744210; border-left: 4px solid #ed8936; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="font-weight: bold; color: #ed8936; margin-bottom: 10px;">⚠️ Warning: This Action Is Permanent</div>
            <div style="color: #e0e0e0; font-size: 14px;">
            Once this certificate is revoked, it cannot be used for any operations. This action is irreversible.
            The certificate will be listed on the Certificate Revocation List (CRL).
            </div>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # Summary
            st.markdown(f"""
            <div style="background-color: #2d3748; border-left: 4px solid #f6ad55; border-radius: 5px; padding: 15px; margin: 15px 0;">
            <div style="font-weight: bold; color: #f6ad55; margin-bottom: 10px;">📋 Revocation Summary</div>
            <div style="color: #e0e0e0; font-size: 14px;">
            <div style="margin: 5px 0;"><strong>Certificate ID:</strong> {selected_cert['id']}</div>
            <div style="margin: 5px 0;"><strong>Serial Number:</strong> {selected_cert['serial_number']}</div>
            <div style="margin: 5px 0;"><strong>Reason:</strong> {reason}</div>
            <div style="margin: 5px 0;"><strong>Request Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)

            confirm = st.checkbox(
                "✓ I understand this action is permanent and cannot be undone",
                key="confirm_revoke"
            )

            if st.button(
                "🚫 Submit Revocation Request",
                disabled=not confirm,
                key="btn_submit_revoke",
                use_container_width=True
            ):
                try:
                    result = api_client.request_revoke_certificate(selected_cert["id"], reason)
                    new_revocation = {
                        "id": result["id"],
                        "cert_id": result["certificate_id"],
                        "serial_number": selected_cert["serial_number"],
                        "reason": result["reason"],
                        "status": result["status"],
                        "timestamp": datetime.now()
                    }
                    st.session_state.revoked_certs.append(new_revocation)

                    st.success(f"""
                    ✅ Revocation Request Submitted Successfully!

                    **Request Details:**
                    - **Request ID:** {result['id']}
                    - **Certificate ID:** {result['certificate_id']}
                    - **Serial Number:** {selected_cert['serial_number']}
                    - **Revocation Reason:** {reason}
                    - **Submitted:** {new_revocation['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

                    Your revocation request has been submitted for admin review.
                    """)
                except http_requests.HTTPError as e:
                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                    st.error(f"❌ Error: {detail}")
                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend.")

    with tab2:
        st.subheader("Revocation Request History (This Session)")

        if not st.session_state.revoked_certs:
            st.info("No revocation requests submitted this session.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("⏳ Pending", len([r for r in st.session_state.revoked_certs if r["status"] == "pending"]))
            with col2:
                st.metric("✅ Approved", len([r for r in st.session_state.revoked_certs if r["status"] == "approved"]))
            with col3:
                st.metric("❌ Rejected", len([r for r in st.session_state.revoked_certs if r["status"] == "rejected"]))
            with col4:
                st.metric("📊 Total", len(st.session_state.revoked_certs))

            st.divider()

            for req in reversed(st.session_state.revoked_certs):
                status_icon = "🟢" if req["status"] == "approved" else ("🟠" if req["status"] == "pending" else "🔴")
                with st.expander(f"{status_icon} Request #{req['id']} - Serial {req['serial_number']} ({req['status'].upper()})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Request ID:** {req['id']}")
                        st.write(f"**Certificate ID:** {req['cert_id']}")
                    with col2:
                        st.write(f"**Reason:** {req['reason']}")
                        st.write(f"**Status:** {req['status'].upper()}")
                    with col3:
                        st.write(f"**Submitted:** {req['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
