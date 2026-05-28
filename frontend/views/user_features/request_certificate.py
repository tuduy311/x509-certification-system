import streamlit as st
import api.api_client as api_client
import requests as http_requests

# CSR is built entirely on the client – private key never leaves this process
from crypto import build_csr



def clear_success():
    if "submit_success" in st.session_state:
        st.session_state.submit_success = None


def request_certificate():

    # ── Session state ──
    if "user_requests" not in st.session_state:
        st.session_state.user_requests = []
    if "generated_csr" not in st.session_state:
        st.session_state.generated_csr = ""
    if "csr_error" not in st.session_state:
        st.session_state.csr_error = None
    if "submit_success" not in st.session_state:
        st.session_state.submit_success = None
    # Cache my_requests – only fetched on first load or explicit refresh
    if "my_requests_cache" not in st.session_state:
        st.session_state.my_requests_cache = None
    if "my_requests_error" not in st.session_state:
        st.session_state.my_requests_error = None

    # ── Back button ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()
    st.title("📤 Request Certificate")
    st.markdown("Fill in your information, paste your key pair, generate a CSR locally, then submit to the CA.")
    st.divider()

    tab1, tab2 = st.tabs(["📝 New Request", "📋 My Requests"])

    # ═══════════════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("Subject Information")
        st.caption("These fields will be embedded in the CSR and ultimately in your certificate.")

        col1, col2 = st.columns(2)

        with col1:
            common_name = st.text_input(
                "Common Name (CN) ✱",
                placeholder="example.com or Your Full Name",
                key="req_cn",
                on_change=clear_success
            )
            organization = st.text_input(
                "Organization (O):",
                placeholder="Your Organization",
                key="req_org",
                on_change=clear_success
            )
            organizational_unit = st.text_input(
                "Organizational Unit (OU):",
                placeholder="IT Department",
                key="req_ou",
                on_change=clear_success
            )

        with col2:
            country = st.text_input(
                "Country Code (C):",
                value="VN",
                max_chars=2,
                key="req_country",
                on_change=clear_success
            )
            state = st.text_input(
                "State / Province (ST):",
                placeholder="Hanoi",
                key="req_state",
                on_change=clear_success
            )
            locality = st.text_input(
                "Locality / City (L):",
                placeholder="Hanoi",
                key="req_locality",
                on_change=clear_success
            )

        st.divider()
        st.subheader("Key Pair")
        st.caption(
            "Paste your RSA or ECC key pair below. "
            "The **private key never leaves your browser** – the CSR is signed locally."
        )

        col_pub, col_priv = st.columns(2)

        with col_pub:
            public_key_pem = st.text_area(
                "Public Key (PEM):",
                placeholder="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
                height=160,
                key="req_pub_key",
                on_change=clear_success
            )

        with col_priv:
            private_key_pem = st.text_area(
                "Private Key (PEM) 🔒:",
                placeholder="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
                height=160,
                key="req_priv_key",
                on_change=clear_success
            )

        st.divider()
        st.subheader("Generate CSR Locally")

        hash_alg = st.selectbox(
            "Hash Algorithm for CSR signature:",
            options=["SHA256", "SHA384", "SHA512"],
            index=0,
            key="req_hash_alg",
            on_change=clear_success
        )

        if st.button("🔄 Convert to CSR", use_container_width=True, key="btn_convert_csr"):
            st.session_state.submit_success = None
            if not common_name.strip():
                st.error("❌ Common Name (CN) is required.")
            elif not private_key_pem.strip():
                st.error("❌ Private Key is required to sign the CSR.")
            else:
                subject = {
                    "common_name": common_name.strip(),
                    "country": country.strip(),
                    "state": state.strip(),
                    "locality": locality.strip(),
                    "organization": organization.strip(),
                    "organizational_unit": organizational_unit.strip(),
                }
                try:
                    csr_pem = build_csr(subject, private_key_pem.strip(), hash_alg)
                    st.session_state.generated_csr = csr_pem
                    st.session_state.csr_error = None
                    st.success("✅ CSR generated successfully! You can review or edit it below before submitting.")
                except ValueError as e:
                    st.session_state.csr_error = str(e)
                    st.session_state.generated_csr = ""

        if st.session_state.csr_error:
            st.error(f"❌ CSR generation failed: {st.session_state.csr_error}")

        st.divider()
        st.subheader("Review & Submit CSR")
        st.caption("The CSR below is editable – you can manually adjust it for testing purposes.")

        csr_pem = st.text_area(
            "Certificate Signing Request (PEM) – editable:",
            value=st.session_state.generated_csr,
            placeholder="-----BEGIN CERTIFICATE REQUEST-----\n...\n-----END CERTIFICATE REQUEST-----",
            height=200,
            key="csr_final_input",
            on_change=clear_success
        )

        # Request purpose (metadata only, not embedded in CSR)
        request_purpose = st.selectbox(
            "Request Purpose:",
            options=[
                "Web Server (TLS/SSL)",
                "Client Authentication",
                "Email (S/MIME)",
                "Code Signing",
                "Other"
            ],
            key="req_purpose",
            on_change=clear_success
        )

        additional_info = st.text_area(
            "Additional Information (optional):",
            placeholder="Add any additional details about your request…",
            key="req_info",
            on_change=clear_success
        )

        st.divider()

        # ── Request summary ──
        csr_ready = bool(csr_pem.strip())
        st.markdown(f"""
        <div style="background-color:#2d3748; border-left:4px solid #4299e1;
                    border-radius:5px; padding:15px; margin:15px 0;">
        <div style="font-weight:bold; color:#4299e1; margin-bottom:10px;">📋 Request Summary</div>
        <div style="color:#e0e0e0; font-size:14px;">
        <div style="margin:5px 0;"><strong>Common Name:</strong> {common_name or '—'}</div>
        <div style="margin:5px 0;"><strong>Organization:</strong> {organization or '—'}</div>
        <div style="margin:5px 0;"><strong>Country:</strong> {country or '—'}</div>
        <div style="margin:5px 0;"><strong>Purpose:</strong> {request_purpose}</div>
        <div style="margin:5px 0;"><strong>CSR Status:</strong> {'✅ Ready' if csr_ready else '⏳ Not generated yet'}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        confirm = st.checkbox("✓ I confirm all information is correct and the CSR is ready", key="confirm_req")

        if st.button(
            "📤 Submit Request",
            disabled=not (confirm and csr_ready),
            key="btn_submit_req",
            use_container_width=True,
            type="primary"
        ):
            cleaned = csr_pem.strip()
            # Basic PEM format check
            if not (cleaned.startswith("-----BEGIN CERTIFICATE REQUEST-----") and
                    cleaned.endswith("-----END CERTIFICATE REQUEST-----")):
                st.error("❌ Invalid CSR format. Must be a valid PEM-encoded Certificate Request.")
            else:
                try:
                    result = api_client.request_certificate(cleaned)
                    st.session_state.user_requests.append(result)
                    st.session_state.submit_success = {
                        "id": result["id"],
                        "status": result["status"],
                        "created_at": str(result["created_at"])[:19]
                    }
                    # Invalidate cache so it refreshes on next view
                    st.session_state.my_requests_cache = None
                    # Clear the CSR after successful submission
                    st.session_state.generated_csr = ""
                except http_requests.HTTPError as e:
                    if e.response is not None:
                        detail = e.response.json().get("detail", str(e))
                        st.error(f"❌ {detail}")
                    else:
                        st.error(f"❌ Error: {str(e)}")
                    st.session_state.submit_success = None
                except http_requests.ConnectionError:
                    st.error("❌ Cannot connect to backend.")
                    st.session_state.submit_success = None

        if st.session_state.submit_success:
            s = st.session_state.submit_success
            st.success(f"""
                ✅ **Certificate Request Submitted Successfully!**

                **Request Details:**
                - **Request ID:** {s['id']}
                - **Status:** {s['status'].upper()}
                - **Submitted:** {s['created_at']}

                Your request is pending admin review. You'll be notified when it is approved or rejected.
            """)
            if st.button("Dismiss Notification", key="btn_dismiss_submit_success", use_container_width=True):
                clear_success()
                st.rerun()

    # ═══════════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("My Certificate Requests")

        col_hdr, col_btn = st.columns([4, 1])
        with col_btn:
            if st.button("🔄 Refresh", key="btn_refresh_requests", use_container_width=True):
                st.session_state.my_requests_cache = None

        # Fetch from backend only when cache is empty
        if st.session_state.my_requests_cache is None:
            try:
                st.session_state.my_requests_cache = api_client.get_my_requests()
                st.session_state.my_requests_error = None
            except http_requests.ConnectionError:
                st.session_state.my_requests_error = "❌ Cannot connect to backend."
            except http_requests.HTTPError as e:
                st.session_state.my_requests_error = f"Backend error: {e}"

        if st.session_state.my_requests_error:
            st.error(st.session_state.my_requests_error)
            return

        user_requests = st.session_state.my_requests_cache or []

        if not user_requests:
            st.info("No certificate requests yet. Submit your first request in the 'New Request' tab.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⏳ Pending",  len([r for r in user_requests if r["status"] == "pending"]))
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
                        st.write(f"**Explanation:** {req['rejection_details']}")
                    with col2:
                        st.write(f"**Created:** {str(req['created_at'])[:19]}")
                        st.write(f"**Reason:** {req['rejection_reason']}")

                    st.divider()
                    st.markdown("**📄 CSR (PEM):**")
                    st.code(req["csr_pem"], language="text")
