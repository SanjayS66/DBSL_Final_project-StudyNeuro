import streamlit as st
import pandas as pd
from db import get_df, run_query, risk_badge, score_color, call_procedure


def show():
    st.markdown("""
    <h1 style='font-size:2.2rem; margin-bottom:0.2rem;'>Wellness Dashboard</h1>
    <p style='color:#888; font-size:0.9rem; margin-bottom:2rem;'>
        Real-time burnout risk across all enrolled students
    </p>
    """, unsafe_allow_html=True)

    # ── Refresh all button ───────────────────────────────────────────────────
    col_btn, col_space = st.columns([1, 5])
    with col_btn:
        if st.button("🔄  Refresh All Scores"):
            with st.spinner("Recalculating burnout scores…"):
                try:
                    call_procedure("Wellness_Pkg.Refresh_All_Students")
                    st.success("All scores updated!")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top KPI row ──────────────────────────────────────────────────────────
    try:
        kpi_df = get_df("""
            SELECT
                COUNT(DISTINCT s.Student_ID)                              AS total_students,
                COUNT(DISTINCT CASE WHEN b.Risk_Level='Critical' 
                               THEN s.Student_ID END)                     AS critical_count,
                COUNT(DISTINCT CASE WHEN b.Risk_Level='High'    
                               THEN s.Student_ID END)                     AS high_count,
                ROUND(AVG(b.Calculated_Risk_Score), 1)                    AS avg_score
            FROM Students s
            LEFT JOIN Burnout_Index b ON s.Student_ID = b.Student_ID
        """)

        total     = int(kpi_df["TOTAL_STUDENTS"].iloc[0] or 0)
        critical  = int(kpi_df["CRITICAL_COUNT"].iloc[0] or 0)
        high      = int(kpi_df["HIGH_COUNT"].iloc[0] or 0)
        avg_score = kpi_df["AVG_SCORE"].iloc[0]

        k1, k2, k3, k4 = st.columns([0.8, 0.8, 0.8, 1.4])
        for col, label, value, color in [
            (k1, "Total Students",   total,     "#0d0d0d"),
            (k2, "Critical Risk",    critical,  "#7f1d1d"),
            (k3, "High Risk",        high,      "#991b1b"),
            (k4, "Avg Burnout Score",
             f"{avg_score:.1f}/100" if avg_score else "—",
             score_color(avg_score)),
        ]:
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.08em;
                                text-transform:uppercase; color:#999;'>{label}</div>
                    <div style='font-size:2rem; font-family:Syne,sans-serif;
                                font-weight:800; color:{color}; margin-top:4px;'>{value}</div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load KPIs: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Student burnout table ────────────────────────────────────────────────
    st.markdown("### All Students — Risk Overview")

    try:
        df = get_df("""
            SELECT
                s.Student_ID,
                s.Name,
                br.Branch_Name                          AS Branch,
                s.Year_of_Study                         AS Year,
                ROUND(b.Calculated_Risk_Score, 1)       AS Score,
                NVL(b.Risk_Level, 'N/A')                AS Risk_Level,
                NVL(b.Confidence_Score, 0)              AS Data_Days,
                TO_CHAR(b.Calculated_At,'DD-Mon HH24:MI') AS Last_Updated
            FROM Students s
            JOIN Branches br ON s.Branch_ID = br.Branch_ID
            LEFT JOIN Burnout_Index b ON s.Student_ID = b.Student_ID
            ORDER BY NVL(b.Calculated_Risk_Score, 0) DESC
        """)

        if df.empty:
            st.info("No student data found. Make sure the database is populated.")
            return

        # Filter controls
        cf1, cf2, cf3 = st.columns([2, 2, 3])
        with cf1:
            branches = ["All"] + sorted(df["BRANCH"].dropna().unique().tolist())
            sel_branch = st.selectbox("Branch", branches, key="dash_branch")
        with cf2:
            risks = ["All", "Critical", "High", "Moderate", "Low", "N/A"]
            sel_risk = st.selectbox("Risk Level", risks, key="dash_risk")
        with cf3:
            search = st.text_input("Search by name", placeholder="Type student name…", key="dash_search")

        if sel_branch != "All":
            df = df[df["BRANCH"] == sel_branch]
        if sel_risk != "All":
            df = df[df["RISK_LEVEL"] == sel_risk]
        if search:
            df = df[df["NAME"].str.contains(search, case=False, na=False)]

        st.markdown("<br>", unsafe_allow_html=True)

        # Render as styled rows
        for _, row in df.iterrows():
            score = row["SCORE"]
            bar_w = int(score) if pd.notna(score) else 0
            bar_color = score_color(score)

            st.markdown(f"""
            <div class='metric-card' style='padding:1rem 1.4rem;'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <span style='font-family:Syne,sans-serif; font-weight:700;
                                     font-size:1rem;'>{row['NAME']}</span>
                        <span style='color:#999; font-size:0.8rem; margin-left:8px;'>
                            #{row['STUDENT_ID']} · {row['BRANCH']} · Year {row['YEAR']}
                        </span>
                    </div>
                    <div style='display:flex; align-items:center; gap:12px;'>
                        {risk_badge(row['RISK_LEVEL'])}
                        <span style='font-family:Syne,sans-serif; font-weight:800;
                                     font-size:1.3rem; color:{bar_color};'>
                            {f"{score:.0f}" if pd.notna(score) else "—"}
                        </span>
                    </div>
                </div>
                <div style='margin-top:8px; background:#f0ede6; border-radius:4px; height:5px;'>
                    <div style='width:{bar_w}%; background:{bar_color};
                                border-radius:4px; height:5px; transition:width 0.4s;'></div>
                </div>
                <div style='margin-top:5px; font-size:0.72rem; color:#aaa;'>
                    {row['DATA_DAYS']} days of data · Updated {row['LAST_UPDATED'] or 'never'}
                </div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading student data: {e}")


# ── Risk distribution bar chart ──────────────────────────────────────────
    st.markdown("<br><h3>Risk Distribution</h3>", unsafe_allow_html=True)
    try:
        # Using double quotes for aliases to avoid Oracle Reserved Word conflicts (Level)
        query = """
            SELECT 
                NVL(b.Risk_Level, 'Not Calculated') AS "LEVEL_NAME", 
                COUNT(*) AS "TOTAL_COUNT"
            FROM Students s
            LEFT JOIN Burnout_Index b ON s.Student_ID = b.Student_ID
            GROUP BY NVL(b.Risk_Level, 'Not Calculated')
            ORDER BY "TOTAL_COUNT" DESC
        """
        dist_df = get_df(query)

        if not dist_df.empty:
            # Update these keys to match the new uppercase aliases from the DF
            color_map = {
                "Low": "#059669", "Moderate": "#d97706",
                "High": "#dc2626", "Critical": "#7f1d1d",
                "Not Calculated": "#9ca3af"
            }
            dist_df["COLOR"] = dist_df["LEVEL_NAME"].map(
                lambda x: color_map.get(x, "#9ca3af")
            )
            # Set the index using the new alias name
            st.bar_chart(dist_df.set_index("LEVEL_NAME")["TOTAL_COUNT"])
            
    except Exception as e:
        st.error(f"SQL Error: {e}") # Changed to error for better visibility during debugging