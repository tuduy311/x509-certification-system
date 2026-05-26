import streamlit as st
from datetime import datetime, timedelta
import api.api_client as api_client
import requests as http_requests


def renew_certificate():

    if "renewed_certificates" not in st.session_state:
        st.session_state.renewed_certificates = []

    # ── Back button (with top margin to avoid Streamlit toolbar overlap) ──
    st.markdown("<div style='margin-top:60px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        st.session_state.current_feature = None
        st.rerun()

    st.divider()

    st.title("🔄 Renew Certificate")
    st.markdown("Renew your expiring or expired certificates")
    st.divider()

    # ── Fetch user's certificates from backend ──
    try:
        all_certs = api_client.get_my_certificates()
    except http_requests.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        all_certs = []
    except http_requests.HTTPError as e:
        st.error(f"Backend error: {e}")
        all_certs = []

    now = datetime.utcnow()

    # Classify certificates
    expiring_soon = []
    for c in all_certs:
        if c["status"] != "approved":
            continue
        try:
            valid_to = datetime.fromisoformat(str(c["valid_to"]).replace("T", " ").split(".")[0])
            if (valid_to - now).days <= 30:
                c["_days_left"] = (valid_to - now).days
                expiring_soon.append(c)
        except Exception:
            pass

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏰ Expiring Soon (≤30d)", len(expiring_soon))
    with col2:
        st.metric("📋 Total Certificates", len(all_certs))
    with col3:
        st.metric("🔄 Renewed Requests", len(st.session_state.renewed_certificates))

    st.divider()

    tab1, tab2 = st.tabs(["🔄 Renew Process", "📊 Expiring Certificates"])

    with tab1:
        st.subheader("How to Renew Your Certificate")

        st.info("""
        **🔄 Certificate Renewal Process:**

        In this CA system, certificate renewal requires submitting a **new CSR request**
        and having it approved by an administrator. Follow these steps:

        1. **Generate a new key pair** – get a fresh RSA key pair from the server
        2. **Create a new CSR** – using your new private key (with `openssl req` or similar)
        3. **Submit the CSR** – paste your CSR in the "Request Certificate" page
        4. **Wait for approval** – an admin will approve/reject your request
        5. **Download your new certificate** – available in "My Certificates" after approval
        """)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔑 1. Generate New Key Pair", use_container_width=True):
                st.session_state.current_feature = "generate_key_pair"
                st.rerun()

        with col2:
            if st.button("📤 2. Submit New CSR Request", use_container_width=True):
                st.session_state.current_feature = "request_certificate"
                st.rerun()

        st.divider()

        st.subheader("Quick CSR Generation Guide")

        with st.expander("🛠️ Generate a CSR with OpenSSL (Command Line)"):
            st.code("""
# Step 1: Generate private key
openssl genrsa -out my_private.key 2048

# Step 2: Create CSR
openssl req -new -key my_private.key -out my_request.csr \\
    -subj "/C=VN/ST=Hanoi/L=Hanoi/O=MyOrganization/CN=example.com"

# Step 3: Display CSR (paste this into the request form)
cat my_request.csr
            """.strip(), language="bash")

        with st.expander("🔑 Or use the built-in key generator"):
            st.markdown("""
            The **Generate Key Pair** feature generates an RSA key pair on the server
            and returns the PEM files to you. You can then use the public key in your CSR.

            Note: You still need to create the CSR locally using the returned private key.
            """)

    with tab2:
        st.subheader("Certificates Expiring Soon (≤ 30 days)")

        if not expiring_soon:
            st.success("✅ All your certificates are valid for more than 30 days.")
        else:
            st.warning(f"⚠️ You have {len(expiring_soon)} certificate(s) expiring within 30 days!")

            for cert in expiring_soon:
                days_left = cert.get("_days_left", "?")
                status_icon = "🔴" if days_left < 7 else "🟡"

                with st.expander(f"{status_icon} Cert #{cert['id']} – {days_left} days left (Valid to: {str(cert['valid_to'])[:10]})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Certificate ID:** {cert['id']}")
                        st.write(f"**Serial Number:** `{cert['serial_number']}`")
                    with col2:
                        st.write(f"**Valid From:** {str(cert['valid_from'])[:10]}")
                        st.write(f"**Valid To:** {str(cert['valid_to'])[:10]}")
                        st.write(f"**Days Left:** {days_left}")

                    if st.button(f"📤 Submit renewal CSR for Cert #{cert['id']}", key=f"renew_goto_{cert['id']}"):
                        st.session_state.current_feature = "request_certificate"
                        st.rerun()

    st.divider()

    st.subheader("📊 Renewal Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔄 Total Renewals Submitted", len(st.session_state.renewed_certificates))
    with col2:
        st.metric("⏰ Expiring Soon", len(expiring_soon))
    with col3:
        st.metric("✅ Total Certs", len([c for c in all_certs if c["status"] == "approved"]))
