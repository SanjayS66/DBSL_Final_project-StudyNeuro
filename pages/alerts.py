import streamlit as st
from db import get_df, run_dml, run_query


def show():
    st.markdown("""
    <h1 style='font-size:2.2rem; margin-bottom:0.2rem;'>Alerts & Interventions</h1>
    <p style='color:#888; font-size:0.9rem; margin-bottom:2rem;'>
        Auto-generated alerts when burnout scores cross High or Critical thresholds
    </p>
    """, unsafe_allow_html=True)

    # ── Summary counts ───────────────────────────────────────────────────────
    try:
        summary_df = get_df("""
            SELECT
                COUNT(*)                                            AS total,
                COUNT(CASE WHEN Alert_Type LIKE '%Critical%' THEN 1 END) AS critical,
                COUNT(CASE WHEN Alert_Type LIKE '%High%' THEN 1 END)     AS high,
                COUNT(DISTINCT Student_ID)                               AS students
            FROM Alerts
            WHERE Created_At >= SYSDATE - 7
        """)
        s = summary_df.iloc[0]
        k1, k2, k3, k4 = st.columns(4)
        for col, lbl, val, clr in [
            (k1, "Alerts (7 days)",      int(s["TOTAL"]),    "#0d0d0d"),
            (k2, "Critical Alerts",      int(s["CRITICAL"]), "#7f1d1d"),
            (k3, "High Risk Alerts",     int(s["HIGH"]),     "#991b1b"),
            (k4, "Students Affected",    int(s["STUDENTS"]), "#1e40af"),
        ]:
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.08em;
                                text-transform:uppercase; color:#999;'>{lbl}</div>
                    <div style='font-size:2rem; font-family:Syne,sans-serif;
                                font-weight:800; color:{clr};'>{val}</div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load summary: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filter controls ──────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filter_type = st.selectbox("Alert Type", ["All", "Critical", "High"], key="al_type")
    with fc2:
        try:
            students_df = get_df("SELECT Student_ID, Name FROM Students ORDER BY Name")
            student_opts = {"All Students": None}
            for _, r in students_df.iterrows():
                student_opts[r["NAME"]] = r["STUDENT_ID"]
            sel_student = st.selectbox("Student", list(student_opts.keys()), key="al_student")
        except Exception:
            sel_student = "All Students"
            student_opts = {"All Students": None}
    with fc3:
        days_back = st.selectbox("Time Range", ["Last 7 days","Last 30 days","All time"],
                                 key="al_time")

    days_map = {"Last 7 days": 7, "Last 30 days": 30, "All time": 9999}
    days_val = days_map[days_back]

    # Build query dynamically
    where_clauses = [f"a.Created_At >= SYSDATE - {days_val}"]
    if filter_type != "All":
        where_clauses.append(f"a.Alert_Type LIKE '%{filter_type}%'")
    if sel_student != "All Students" and student_opts[sel_student]:
        where_clauses.append(f"a.Student_ID = {student_opts[sel_student]}")

    where_sql = " AND ".join(where_clauses)

    st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)
    st.markdown("### Alert Log")

    try:
        alerts_df = get_df(f"""
            SELECT
                a.Alert_ID,
                s.Name                                        AS Student,
                a.Alert_Type,
                ROUND(a.Triggered_Score, 1)                  AS Score,
                NVL(a.Intervention, '—')                     AS Intervention,
                TO_CHAR(a.Created_At,'DD-Mon-YYYY HH24:MI')  AS Generated_At
            FROM Alerts a
            JOIN Students s ON a.Student_ID = s.Student_ID
            WHERE {where_sql}
            ORDER BY a.Created_At DESC
        """)

        if alerts_df.empty:
            st.info("No alerts found for the selected filters.")
        else:
            for _, row in alerts_df.iterrows():
                is_critical = "Critical" in str(row["ALERT_TYPE"])
                border_color = "#7f1d1d" if is_critical else "#991b1b"
                icon = "🔴" if is_critical else "🟠"

                st.markdown(f"""
                <div class='metric-card' style='padding:0.9rem 1.3rem;
                            border-left:4px solid {border_color}; margin-bottom:0.6rem;'>
                    <div style='display:flex; justify-content:space-between;
                                align-items:flex-start;'>
                        <div>
                            <span style='font-size:1rem;'>{icon}</span>
                            <span style='font-family:Syne,sans-serif; font-weight:700;
                                         margin-left:6px;'>{row['STUDENT']}</span>
                            <span style='color:#999; font-size:0.82rem;
                                         margin-left:8px;'>{row['ALERT_TYPE']}</span>
                        </div>
                        <div style='text-align:right;'>
                            <div style='font-family:Syne,sans-serif; font-weight:800;
                                        font-size:1.2rem; color:{border_color};'>
                                {row['SCORE']}
                            </div>
                            <div style='font-size:0.72rem; color:#aaa;'>
                                {row['GENERATED_AT']}
                            </div>
                        </div>
                    </div>
                    <div style='margin-top:6px; padding:6px 10px; background:#f7f5f0;
                                border-radius:6px; font-size:0.82rem; color:#555;'>
                        💡 {row['INTERVENTION']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Alert trend chart
        st.markdown("<br><h4>Alert Frequency Over Time</h4>", unsafe_allow_html=True)
        try:
            trend_df = get_df("""
                SELECT TO_CHAR(TRUNC(Created_At),'DD-Mon') AS Day,
                       COUNT(*) AS Alerts
                FROM Alerts
                WHERE Created_At >= SYSDATE - 30
                GROUP BY TRUNC(Created_At)
                ORDER BY TRUNC(Created_At)
            """)
            if not trend_df.empty:
                st.bar_chart(trend_df.set_index("DAY")["ALERTS"])
        except Exception as e:
            st.caption(f"Trend chart unavailable: {e}")

    except Exception as e:
        st.error(f"Error loading alerts: {e}")

    # ── Manual alert creation ────────────────────────────────────────────────
    st.markdown("<hr style='margin:2rem 0 1rem;'>", unsafe_allow_html=True)
    st.markdown("### Create Manual Alert")
    with st.expander("➕ Add a manual intervention note"):
        try:
            students_df2 = get_df("SELECT Student_ID, Name FROM Students ORDER BY Name")
            s_map = {r["NAME"]: r["STUDENT_ID"] for _, r in students_df2.iterrows()}
            sel_s  = st.selectbox("Student", list(s_map.keys()), key="man_student")
            a_type = st.text_input("Alert Type", value="Manual Review", key="man_type")
            interv = st.text_area("Intervention / Notes", key="man_notes")

            if st.button("💾  Save Alert", key="save_manual_alert"):
                if not interv.strip():
                    st.warning("Please enter an intervention note.")
                else:
                    _, rows = run_query("SELECT Alert_Seq.NEXTVAL FROM DUAL")
                    new_id = rows[0][0]
                    run_dml("""
                        INSERT INTO Alerts
                            (Alert_ID, Student_ID, Alert_Type,
                             Triggered_Score, Intervention, Created_At)
                        VALUES (:1, :2, :3, NULL, :4, SYSTIMESTAMP)
                    """, [new_id, s_map[sel_s], a_type, interv.strip()])
                    st.success("✅ Manual alert saved.")
        except Exception as e:
            st.error(f"Error: {e}")