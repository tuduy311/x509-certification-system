import streamlit as st
from datetime import datetime
import api_client
import requests as http_requests


def approve_requests():
    # Initialize session state
    if "approval_data" not in st.session_state:
        st.session_state.approval_data = {}

    # ── Back to Dashboard button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    # Header Section
    st.title("✅ Approve Certificate Requests")
    st.markdown("Manage and approve pending X.509 certificate requests")
    st.divider()

    # ── Fetch requests from backend ──
    try:
        all_requests = api_client.get_all_requests()
    except http_requests.ConnectionError:
        st.error("❌ Cannot connect to backend. Is the server running at http://localhost:8000?")
        return
    except http_requests.HTTPError as e:
        st.error(f"Backend error: {e}")
        return

    # Filter PENDING requests only
    pending_requests = [r for r in all_requests if r["status"] == "pending"]

    if not pending_requests:
        st.info("ℹ️ No pending certificate requests at the moment.")
        return

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔄 Total Pending", len(pending_requests))
    with col2:
        st.metric("📋 Total Requests", len(all_requests))
    with col3:
        approved_count = len([r for r in all_requests if r["status"] == "approved"])
        st.metric("✅ Approved", approved_count)

    st.divider()

    # Request Selection
    st.subheader("Select Request")

    request_options = [
        f"Request #{r['id']} - User {r['user_id']} (Created: {r['created_at'][:16]})"
        for r in pending_requests
    ]

    selected_option = st.selectbox(
        "Choose a certificate request to review:",
        range(len(pending_requests)),
        format_func=lambda i: request_options[i],
        key="request_select"
    )

    selected_request = pending_requests[selected_option]

    st.divider()

    # Request Details
    st.subheader("Request Details")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Request ID:** {selected_request['id']}")
        st.write(f"**User ID:** {selected_request['user_id']}")

    with col2:
        st.write(f"**Status:** {selected_request['status'].upper()}")
        st.write(f"**Created:** {selected_request['created_at'][:19]}")

    with st.expander("📄 View CSR (PEM)"):
        st.code(selected_request["csr_pem"], language="text")

    st.divider()

    # Approval Configuration
    st.subheader("Approval Configuration")

    # Fetch configuration for default settings
    try:
        sys_config = api_client.get_config()
    except Exception:
        sys_config = {}

    col1, col2 = st.columns(2)

    with col1:
        default_val_days = int(sys_config.get("default_validity_days", 365))
        validity_days = st.number_input(
            "Certificate Validity (days)",
            min_value=1,
            max_value=3650,
            value=default_val_days,
            step=1,
            help="How many days should this certificate be valid?"
        )

    with col2:
        default_hash_algo = sys_config.get("hash_algorithm", "SHA256")
        hash_list = ["SHA256", "SHA384", "SHA512"]
        if default_hash_algo not in hash_list:
            hash_list.append(default_hash_algo)
        hash_list = sorted(list(set(hash_list)))

        hash_algorithm = st.selectbox(
            "Hash Algorithm",
            hash_list,
            index=hash_list.index(default_hash_algo) if default_hash_algo in hash_list else 0,
            help="Select the hash algorithm for the certificate"
        )

    # Approval button
    if st.button("✅ Approve Certificate", type="primary"):
        try:
            result = api_client.approve_request(
                request_id=selected_request["id"],
                validity_days=validity_days,
                hash_alg=hash_algorithm
            )
            approval_key = f"request_{selected_request['id']}"
            st.session_state.approval_data[approval_key] = {
                "request_id": selected_request["id"],
                "validity_days": validity_days,
                "hash_algorithm": hash_algorithm,
                "approved_at": datetime.now(),
                "cert_id": result.get("id")
            }
            st.success(
                f"✅ Certificate Request #{selected_request['id']} approved successfully!\n\n"
                f"**New Certificate ID:** {result.get('id')}\n"
                f"**Serial Number:** {result.get('serial_number')}\n"
                f"**Valid Until:** {str(result.get('valid_to', ''))[:10]}\n"
                f"**Hash Algorithm:** {hash_algorithm}"
            )
        except http_requests.HTTPError as e:
            detail = e.response.json().get("detail", str(e)) if e.response else str(e)
            st.error(f"❌ Error: {detail}")
        except http_requests.ConnectionError:
            st.error("❌ Cannot connect to backend.")

    st.divider()

    # Summary
    st.subheader("Approval Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Current Selection:**")
        st.write(f"- Request ID: {selected_request['id']}")
        st.write(f"- Validity: {validity_days} days")
        st.write(f"- Algorithm: {hash_algorithm}")

    with col2:
        st.write("**Previously Approved (this session):**")
        if st.session_state.approval_data:
            for key, data in st.session_state.approval_data.items():
                st.write(f"- Request #{data['request_id']} → Cert #{data.get('cert_id', '?')} ✅")
        else:
            st.write("- None yet")

    st.divider()
