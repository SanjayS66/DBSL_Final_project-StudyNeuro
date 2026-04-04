import oracledb
import streamlit as st
import pandas as pd

# ── Connection ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_connection():
    """
    Returns a persistent Oracle connection.
    Edit the credentials below to match your local Oracle XE setup.
    """
    try:
        conn = oracledb.connect(
            user="system",       # ← change this
            password="password",   # ← change this
            dsn="localhost:1521/XEPDB1" # ← change service name if needed
        )
        return conn
    except oracledb.DatabaseError as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()


def get_df(sql: str, params=None) -> pd.DataFrame:
    """Run a SELECT and return a DataFrame."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params or [])
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows, columns=cols)


def run_query(sql: str, params=None):
    """Run a SELECT and return (column_names, rows)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params or [])
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    cur.close()
    return cols, rows


def run_dml(sql: str, params=None):
    """Run INSERT / UPDATE / DELETE and commit."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params or [])
    conn.commit()
    cur.close()


def call_procedure(proc_name: str, params=None):
    """Call a stored PL/SQL procedure."""
    conn = get_connection()
    cur = conn.cursor()
    cur.callproc(proc_name, params or [])
    conn.commit()
    cur.close()


def call_function(func_name: str, return_type, params=None):
    """Call a stored PL/SQL function and return its value."""
    conn = get_connection()
    cur = conn.cursor()
    result = cur.callfunc(func_name, return_type, params or [])
    cur.close()
    return result


# ── Risk level helpers ───────────────────────────────────────────────────────
RISK_COLORS = {
    "Low":      ("#d1fae5", "#065f46"),
    "Moderate": ("#fef3c7", "#92400e"),
    "High":     ("#fee2e2", "#991b1b"),
    "Critical": ("#1a0000", "#ff4d4d"),
    "N/A":      ("#f3f4f6", "#6b7280"),
}

RISK_EMOJI = {
    "Low": "🟢", "Moderate": "🟡", "High": "🟠", "Critical": "🔴", "N/A": "⚪"
}


def risk_badge(level: str) -> str:
    bg, fg = RISK_COLORS.get(level, ("#eee", "#333"))
    return (f'<span style="background:{bg}; color:{fg}; padding:3px 10px; '
            f'border-radius:20px; font-size:0.78rem; font-weight:600;">'
            f'{RISK_EMOJI.get(level,"")} {level}</span>')


def score_color(score) -> str:
    if score is None:
        return "#aaa"
    s = float(score)
    if s < 25:   return "#059669"
    if s < 50:   return "#d97706"
    if s < 75:   return "#dc2626"
    return "#7f1d1d"