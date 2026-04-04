import streamlit as st

st.set_page_config(
    page_title="MindMetrics — Student Wellness",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d0d0d;
    border-right: 1px solid #1f1f1f;
}
section[data-testid="stSidebar"] * {
    color: #e8e8e8 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.9rem;
    padding: 6px 0;
    letter-spacing: 0.02em;
}

/* Main background */
.main .block-container {
    background: #f7f5f0;
    padding-top: 2rem;
}

/* Headings */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
}

/* Cards */
/* Updated Cards CSS in app.py */
.metric-card {
    background: #ffffff;
    border: 1px solid #e8e5de;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    color: #1a1a1a; /* Adds a dark charcoal color to all text inside the card */
}

.metric-card h1, .metric-card h2, .metric-card h3 {
    color: #0d0d0d !important; /* Forces headings to be deep black */
}

.metric-card .sub-text {
    color: #666666; /* For that "7 days of data" and student ID line */
    font-size: 0.85rem;
}

/* Risk badge colors */
.badge-low      { background:#d1fae5; color:#065f46; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-moderate { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-high     { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-critical { background:#1a0000; color:#ff4d4d; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* Buttons */
.stButton > button {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    letter-spacing: 0.04em;
    border-radius: 8px;
    background: #0d0d0d;
    color: #f7f5f0;
    border: none;
    padding: 0.5rem 1.4rem;
    transition: background 0.2s;
}
.stButton > button:hover {
    background: #333;
    color: #fff;
}

/* Selectbox / sliders */
.stSelectbox label, .stSlider label, .stDateInput label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    font-weight: 500;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* Dividers */
hr { border-color: #e8e5de; }

/* Success / info messages */
.stSuccess, .stInfo { border-radius: 8px; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f7f5f0; }
::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar nav ─────────────────────────────────────────────────────────────
with st.sidebar:
    # Corrected CSS placement
    st.markdown("""
        <style>
            /* This hides the default Streamlit nav list */
            [data-testid="stSidebarNav"] {
                display: none !important;
            }
        </style>
        
        <div style='padding: 1.2rem 0 2rem 0;'>
            <div style='font-family: Syne, sans-serif; font-size: 1.5rem;
                        font-weight: 800; color: #f7f5f0; letter-spacing:-0.03em;'>
                🧠 MindMetrics
            </div>
            <div style='font-size: 0.75rem; color: #666; margin-top:2px;
                        letter-spacing:0.08em; text-transform:uppercase;'>
                Student Wellness Tracker
            </div>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏠  Dashboard",
         "📝  Log Entry",
         "👤  Student Profile",
         "📅  Assessments",
         "🚨  Alerts",
         "⚙️  Admin"],
        label_visibility="collapsed"
    )

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.7rem; color:#444; line-height:1.7;'>
        CSE 2241 — Database Systems Lab<br>
        MIT Manipal · 2024-25
    </div>
    """, unsafe_allow_html=True)

# ── Route to page ────────────────────────────────────────────────────────────
if   "Dashboard"   in page:
    from pages.dashboard    import show; show()
elif "Log Entry"   in page:
    from pages.log_entry    import show; show()
elif "Student"     in page:
    from pages.student_view import show; show()
elif "Assessment"  in page:
    from pages.assessments  import show; show()
elif "Alerts"      in page:
    from pages.alerts       import show; show()
elif "Admin"       in page:
    from pages.admin        import show; show()