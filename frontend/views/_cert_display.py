"""
frontend/views/_cert_display.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Render parsed X.509 certificate info using native Streamlit components only.
No HTML is used — avoids raw-HTML display issues.

Display format:
  Status banner via st.success / st.error / st.warning
  Certificate body via st.code() — dark, monospace, aligned columns
"""
import streamlit as st


# Column width for the label (pad to align values)
_LABEL_WIDTH = 28


def _fmt_row(label: str, value: str) -> str:
    """Return a single padded key: value line."""
    return f"    {label:<{_LABEL_WIDTH}}{value}"


def _fmt_section(title: str, rows: dict) -> str:
    """Return a section block as a plain-text string."""
    lines = [f"{title}:", ""]
    for label, value in rows.items():
        lines.append(_fmt_row(label, value))
    lines.append("")          # blank line after section
    return "\n".join(lines)


def render_certificate(info: dict, cert_meta: dict | None = None) -> None:
    """
    Render parsed certificate info with native Streamlit widgets.

    Parameters
    ----------
    info      : dict from GET /certificates/{id}/info
                Keys: Basic Details, Issued To, Issued By,
                      Validity Period, SHA-256 Fingerprints
    cert_meta : optional raw cert record for the status banner.
    """
    # ── Status banner ─────────────────────────────────────────────────────────
    if cert_meta:
        status = cert_meta.get("status", "").upper()
        cn     = info.get("Issued To", {}).get("Common Name (CN)", "—")
        banner = f"🔐 {cn}  |  Cert #{cert_meta.get('id', '—')}  |  {status}"
        if status == "APPROVED":
            st.success(banner)
        elif status == "REVOKED":
            st.error(banner)
        elif status == "EXPIRED":
            st.warning(banner)
        else:
            st.info(banner)

    # ── Build plain-text certificate body ────────────────────────────────────
    lines = []

    # Basic Details
    basic = info.get("Basic Details", {})
    if basic:
        lines.append(_fmt_section("Basic Details", basic))

    # Issued To
    issued_to = info.get("Issued To", {})
    if issued_to:
        lines.append(_fmt_section("Issued To", issued_to))

    # Issued By
    issued_by = info.get("Issued By", {})
    if issued_by:
        lines.append(_fmt_section("Issued By", issued_by))

    # Validity Period
    validity = info.get("Validity Period", {})
    if validity:
        lines.append(_fmt_section("Validity Period", validity))

    # SHA-256 Fingerprints — long hashes, each on its own line
    fps = info.get("SHA-256 Fingerprints", {})
    if fps:
        fp_lines = ["SHA-256 Fingerprints:", ""]
        for label, value in fps.items():
            fp_lines.append(f"    {label}:")
            fp_lines.append(f"        {value}")
            fp_lines.append("")
        lines.append("\n".join(fp_lines))

    cert_text = "\n".join(lines)

    # ── Display as a code block (dark bg, monospace, no HTML) ─────────────────
    st.code(cert_text, language=None)
