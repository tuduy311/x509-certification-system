Dashboard_CSS = """
<style>
    .admin-header {
        display: flex;
        justify-content: space-between;
        align-items:center;
        padding:15px 20px;
        border-radius:16px;
        background:rgba(255,255,255,0.1);
        margin-bottom:0;
    }

    .admin-header span {
        color: #FFFFFF !important;
    }

    .admin-header div {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff !important;
    }

    .admin-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        color: #fca5a5;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }

    /* container của toàn bộ tab */
    div[data-baseweb="tab-list"] {
        justify-content: center !important;
        gap: 15px;
    }
    
    /* Tab button */
    button[data-baseweb="tab"] {
        padding: 0 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.1) !important;
    }

    /* TEXT trong tab */
    button[data-baseweb="tab"] * {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #CBD5E1 !important;
    }

    /* Tab đang active */
    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(59,130,246,0.2);
        border-radius: 10px;

        transform: scale(1.1);  
        padding: 18px 18px !important;
    }

    
    /* subheader */
    h3, h3 * {
        color: rgb(93, 203, 239, 0.5) !important;
    }

    .admin-card {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 10px;
    }

    .admin-title {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff !important;
    }

    [data-testid="column"] .stButton > button {
        margin-bottom: 24px !important;
    }

    .admin-content {
        font-size: 16px;
        color: #cbd5e1;
        line-height: 2;
    }

    .user-badge {
        display: inline-block;
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid #22c55e;
        color: #86efac;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
   
</style>
"""