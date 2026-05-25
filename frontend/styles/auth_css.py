AUTH_CSS = """
<style>
/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Auth Panel Wrappers ── */
.auth-left-panel {
    background: #0f1a33;
    border: 2px solid rgba(255, 255, 255, 0.5);
    #border: 2px solid rgba(102, 126, 234, 0.5);

    border-radius: 14px;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);    
    padding: 40px 32px;
    min-height: 560px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.auth-left-panel > div:first-child,
.auth-left-panel > div:last-child {
    position: relative;
    z-index: 1;
}

.auth-panel-logo {
    width: 48px;
    height: 48px;
    background: rgba(255,255,255,0.15);
    border: 0.5px solid rgba(255,255,255,0.25);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 24px;
}

.auth-panel-title {
    font-size: 22px;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}

.auth-panel-subtitle {
    font-size: 15px;
    color: rgba(199,210,254,0.85);
    line-height: 1.6;
}

.auth-panel-status {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 16px;
}

.auth-panel-status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22c55e;
    flex-shrink: 0;
}

.auth-panel-status-text {
    font-size: 12px;
    color: rgba(199,210,254,0.7);
    font-weight: 500;
}

.auth-panel-features {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.auth-panel-feature {
    background: rgba(255,255,255,0.08);
    border: 0.5px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.auth-panel-feature-icon {
    font-size: 13px;
}

.auth-panel-feature-text {
    font-size: 12px;
    color: rgba(199,210,254,0.85);
}


/* ── Inputs ── */
.stTextInput input {
    background: #ffffff !important;
    border: 0.5px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    color: #374151 !important;
    padding: 10px 12px !important;
}
.stTextInput input::placeholder { color: #9ca3af !important; }
.stTextInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
.stTextInput label {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
}



div[data-testid="column"]:nth-of-type(3) {
    background: #0f1a33 !important;
    border: 2px solid rgba(255, 255, 255, 0.5);
    border-radius: 16px !important;
    padding: 50px !important;s
}

div[data-testid="column"]:nth-of-type(3) 
div[data-testid="column"]:nth-of-type(1) .stButton > button,
div[data-testid="column"]:nth-of-type(3) 
div[data-testid="column"]:nth-of-type(2) .stButton > button {
    background: #405b96 !important;
}

</style>
"""


LEFT_PANEL = """
<div class="auth-left-panel">
    <div>
        <div class="auth-panel-logo">🔐</div>
        <div class="auth-panel-title">X.509 Certificate System</div>
        <div class="auth-panel-subtitle">Hệ thống cấp phát<br>chứng chỉ số an toàn</div>
    </div>
    <div>
        <div class="auth-panel-status">
            <div class="auth-panel-status-dot"></div>
            <span class="auth-panel-status-text">Hệ thống hoạt động bình thường</span>
        </div>
        <div class="auth-panel-features">
            <div class="auth-panel-feature">
                <span class="auth-panel-feature-icon">🔒</span>
                <span class="auth-panel-feature-text">Mã hóa RSA 2048-bit</span>
            </div>
            <div class="auth-panel-feature">
                <span class="auth-panel-feature-icon">📋</span>
                <span class="auth-panel-feature-text">Chuẩn X.509 v3</span>
            </div>
            <div class="auth-panel-feature">
                <span class="auth-panel-feature-icon">⚡</span>
                <span class="auth-panel-feature-text">Cấp phát tức thời</span>
            </div>
        </div>
    </div>
</div>
"""