import streamlit as st
from datetime import datetime
import api_client
import requests as http_requests


def request_certificate():

    # Initialize session state
    if "user_requests" not in st.session_state:
        st.session_state.user_requests = []

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("📤 Request Certificate")
    st.markdown("Submit a new certificate request with your Certificate Signing Request (CSR)")
    st.divider()

    tab1, tab2 = st.tabs(["📝 New Request", "📋 My Requests"])

    with tab1:
        st.subheader("Create Certificate Request")

        col1, col2 = st.columns(2)

        with col1:
            common_name = st.text_input(
                "Common Name (CN):",
                placeholder="example.com or your name",
                key="req_cn"
            )

            organization = st.text_input(
                "Organization (O):",
                placeholder="Your Organization",
                key="req_org"
            )

        with col2:
            country = st.text_input(
                "Country Code (C):",
                value="VN",
                max_chars=2,
                key="req_country"
            )

            state = st.text_input(
                "State/Province (ST):",
                placeholder="Hanoi",
                key="req_state"
            )

        st.divider()

        st.markdown("**📄 Certificate Signing Request (CSR):**")

        csr_pem = st.text_area(
            "Paste your CSR in PEM format:",
            placeholder="-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
            height=150,
            key="csr_input"
        )

        st.divider()

        request_purpose = st.selectbox(
            "Request Purpose:",
            options=[
                "Web Server (TLS/SSL)",
                "Client Authentication",
                "Email (S/MIME)",
                "Code Signing",
                "Other"
            ],
            key="req_purpose"
        )

        additional_info = st.text_area(
            "Additional Information (optional):",
            placeholder="Add any additional details about your request...",
            key="req_info"
        )

        st.divider()

        st.markdown(f"""
        <div style="background-color: #2d3748; border-left: 4px solid #4299e1; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <div style="font-weight: bold; color: #4299e1; margin-bottom: 10px;">📋 Request Summary</div>
        <div style="color: #e0e0e0; font-size: 14px;">
        <div style="margin: 5px 0;"><strong>Common Name:</strong> {common_name if common_name else 'Not specified'}</div>
        <div style="margin: 5px 0;"><strong>Organization:</strong> {organization if organization else 'Not specified'}</div>
        <div style="margin: 5px 0;"><strong>Purpose:</strong> {request_purpose}</div>
        <div style="margin: 5px 0;"><strong>CSR Status:</strong> {'✅ Provided' if csr_pem else '⏳ Pending'}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        confirm = st.checkbox(
            "✓ I confirm this certificate request",
            key="confirm_req"
        )

        if st.button(
            "📤 Submit Request",
            disabled=not (confirm and csr_pem.strip()),
            key="btn_submit_req",
            use_container_width=True
        ):
            # Validate CSR format
            cleaned = csr_pem.strip()
            if not (cleaned.startswith("-----BEGIN CERTIFICATE REQUEST-----") and
                    cleaned.endswith("-----END CERTIFICATE REQUEST-----")):
                st.error("❌ Invalid CSR format. Please paste a valid PEM-encoded CSR.")
            else:
                try:
                    result = api_client.request_certificate(cleaned)
                    st.session_state.user_requests.append(result)
                    st.success(f"""
                    ✅ Certificate Request Submitted Successfully!

                    **Request Details:**
                    - **Request ID:** {result['id']}
                    - **Status:** {result['status'].upper()}
                    - **Submitted:** {str(result['created_at'])[:19]}

                    Your request has been submitted for admin review. You will be notified when it is approved or rejected.
                    """)
                except http_requests.HTTPError as e:
                    detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                    st.error(f"❌ Error: {detail}")
                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend.")

    with tab2:
        st.subheader("My Certificate Requests")

        try:
            user_requests = api_client.get_my_requests()
        except http_requests.ConnectionError:
            st.error("❌ Cannot connect to backend.")
            return
        except http_requests.HTTPError as e:
            st.error(f"Backend error: {e}")
            return

        if not user_requests:
            st.info("No certificate requests yet. Submit your first request in the 'New Request' tab.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⏳ Pending", len([r for r in user_requests if r["status"] == "pending"]))
            with col2:
                st.metric("✅ Approved", len([r for r in user_requests if r["status"] == "approved"]))
            with col3:
                st.metric("❌ Rejected", len([r for r in user_requests if r["status"] == "rejected"]))

            st.divider()

            for req in reversed(user_requests):
                status_map = {"approved": "🟢", "pending": "🟠", "rejected": "🔴"}
                icon = status_map.get(req["status"], "⚪")

                with st.expander(f"{icon} Request #{req['id']} – {req['status'].upper()} – {str(req['created_at'])[:10]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Request ID:** {req['id']}")
                        st.write(f"**Status:** {req['status'].upper()}")
                    with col2:
                        st.write(f"**Created:** {str(req['created_at'])[:19]}")

                    st.divider()
                    st.markdown("**📄 CSR (PEM):**")
                    st.code(req["csr_pem"], language="text")
