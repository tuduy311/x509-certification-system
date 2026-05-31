import streamlit as st
from datetime import datetime
import api.api_client as api_client
import requests as http_requests
from api.helpers import BackendError


def revoke_certificate():

    # Initialize session state
    if "admin_revoked_certs" not in st.session_state:
        st.session_state.admin_revoked_certs = []

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("🚫 Revoke Certificate")
    st.markdown("Revoke active certificates immediately")
    st.divider()

    # ── Fetch certificates from backend ──
    try:
        all_certificates = api_client.get_all_certificates()
    except (BackendError, http_requests.ConnectionError):
        return

    # Filter active certificates only (status == "approved" in DB)
    active_certificates = [c for c in all_certificates if c["status"] == "approved"]

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Active", len(active_certificates))
    with col2:
        st.metric("🚫 Revoked", len([c for c in all_certificates if c["status"] == "revoked"]))
    with col3:
        st.metric("⏰ Expired", len([c for c in all_certificates if c["status"] == "expired"]))
    with col4:
        st.metric("📋 Total", len(all_certificates))

    st.divider()

    if not active_certificates:
        st.info("ℹ️ No active certificates available to revoke.")
        return

    # Certificate Selection
    st.subheader("Select Certificate")

    cert_options = [
        f"Cert #{c['id']} - User {c['user_id']} - {c['serial_number']} (Valid to: {str(c['valid_to'])[:10]})"
        for c in active_certificates
    ]

    selected_option = st.selectbox(
        "Choose a certificate to revoke:",
        range(len(active_certificates)),
        format_func=lambda i: cert_options[i],
        key="cert_select"
    )

    selected_cert = active_certificates[selected_option]

    st.divider()

    # Certificate Details
    st.subheader("Certificate Details")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Certificate ID:** {selected_cert['id']}")
        st.write(f"**Request ID:** {selected_cert.get('request_id', 'N/A')}")
        st.write(f"**User ID:** {selected_cert['user_id']}")
        st.write(f"**Serial Number:** `{selected_cert['serial_number']}`")

    with col2:
        st.write(f"**Status:** {selected_cert['status'].upper()}")
        st.write(f"**Valid From:** {str(selected_cert['valid_from'])[:10]}")
        st.write(f"**Valid To:** {str(selected_cert['valid_to'])[:10]}")

    # Certificate PEM
    with st.expander("📄 View Certificate PEM"):
        st.code(selected_cert["cert_pem"], language="text")

    st.divider()

    # Revocation Reason
    st.subheader("Revocation Reason")

    revocation_reason = st.selectbox(
        "Select revocation reason:",
        [
            "Key Compromise",
            "CA Compromise",
            "Affiliation Changed",
            "Superseded",
            "Cessation of Operation",
            "Certificate Hold",
            "Remove from CRL",
            "Privilege Withdrawn",
            "AA Compromise",
            "Other"
        ],
        help="Select the reason for revoking this certificate"
    )

    additional_details = st.text_area(
        "Additional Details (Optional)",
        placeholder="Enter any additional information about this revocation...",
        height=100,
    )

    # Warning
    st.warning(
        f"**Warning:** This action will immediately revoke certificate #{selected_cert['id']}. "
        f"This certificate will no longer be valid and cannot be undone. "
        f"Users depending on this certificate will be affected.",
        icon="⚠️"
    )

    # Confirm Revocation
    st.subheader("Confirm Revocation")

    confirm = st.checkbox(
        "I confirm I want to revoke this certificate",
        help="Check this box to enable the revoke button"
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(
            "🚫 Revoke Certificate",
            use_container_width=True,
            type="primary",
            disabled=not confirm
        ):
            try:
                api_client.admin_revoke_certificate(selected_cert["id"])
                revocation_record = {
                    "cert_id": selected_cert["id"],
                    "user_id": selected_cert["user_id"],
                    "serial_number": selected_cert["serial_number"],
                    "reason": revocation_reason,
                    "details": additional_details,
                    "revoked_at": datetime.now()
                }
                st.session_state.admin_revoked_certs.append(revocation_record)
                st.success(
                    f"Certificate #{selected_cert['id']} revoked successfully!\n\n"
                    f"**Details:**\n"
                    f"- User ID: {selected_cert['user_id']}\n"
                    f"- Serial Number: {selected_cert['serial_number']}\n"
                    f"- Revocation Reason: {revocation_reason}\n"
                    f"- Revoked At: {revocation_record['revoked_at'].strftime('%Y-%m-%d %H:%M:%S')}",
                    icon="✅"
                )
                st.info(
                    "📌 The certificate has been added to the Certificate Revocation List (CRL). "
                    "Generate a new CRL to publish the update.",
                    icon="ℹ️"
                )
            except (BackendError, http_requests.ConnectionError):
                pass

    st.divider()

    # Summary
    st.subheader("Revocation Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Current Selection:**")
        st.write(f"- Certificate ID: {selected_cert['id']}")
        st.write(f"- Serial Number: {selected_cert['serial_number']}")
        st.write(f"- Reason: {revocation_reason}")

    with col2:
        st.write("**Previously Revoked (this session):**")
        if st.session_state.admin_revoked_certs:
            for revoked in st.session_state.admin_revoked_certs:
                st.write(f"- Cert #{revoked['cert_id']} ({revoked['reason']}) ✅")
        else:
            st.write("- None yet")

    st.divider()
