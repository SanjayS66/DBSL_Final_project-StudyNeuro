import streamlit as st
import pandas as pd
from db import get_df, call_procedure, risk_badge, score_color


def show():
    st.markdown("""
    <h1 style='font-size:2.2rem; margin-bottom:0.2rem;'>Student Profile</h1>
    <p style='color:#888; font-size:0.9rem; margin-bottom:2rem;'>
        Deep-dive wellness analytics for an individual student
    </p>
    """, unsafe_allow_html=True)

    # Student selector
    students_df = get_df("SELECT Student_ID, Name FROM Students ORDER BY Name")
    if students_df.empty:
        st.warning("No students found.")
        return

    student_map = {r["NAME"]: r["STUDENT_ID"] for _, r in students_df.iterrows()}
    sel_name   = st.selectbox("Select Student", list(student_map.keys()))
    student_id = student_map[sel_name]

    # Recalculate button
    if st.button("🔄  Recalculate Score"):
        try:
            call_procedure("Refresh_Burnout_Index", [student_id])
            st.success("Score refreshed!")
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)

    # ── Student info header ──────────────────────────────────────────────────
    try:
        info_df = get_df("""
            SELECT s.Student_ID, s.Name,
                   br.Branch_Name,
                   s.Year_of_Study,
                   TO_CHAR(s.Date_of_Joining,'DD-Mon-YYYY') AS Joined,
                   ROUND(NVL(b.Calculated_Risk_Score,0),1)  AS Score,
                   NVL(b.Risk_Level,'N/A')                  AS Risk_Level,
                   NVL(b.Confidence_Score,0)                AS Confidence,
                   TO_CHAR(b.Calculated_At,'DD-Mon-YYYY HH24:MI') AS Updated_At
            FROM Students s
            JOIN Branches br ON s.Branch_ID = br.Branch_ID
            LEFT JOIN Burnout_Index b ON s.Student_ID = b.Student_ID
            WHERE s.Student_ID = :1
        """, [student_id])

        if not info_df.empty:
            r = info_df.iloc[0]
            score = r["SCORE"]
            lvl   = r["RISK_LEVEL"]

            h1, h2 = st.columns([3, 2])
            with h1:
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-family:Syne,sans-serif; font-size:1.5rem;
                                font-weight:800;'>{r['NAME']}</div>
                    <div style='color:#999; font-size:0.85rem; margin:4px 0 10px;'>
                        ID #{r['STUDENT_ID']} &nbsp;·&nbsp;
                        {r['BRANCH_NAME']} &nbsp;·&nbsp;
                        Year {r['YEAR_OF_STUDY']} &nbsp;·&nbsp;
                        Joined {r['JOINED']}
                    </div>
                    {risk_badge(lvl)}
                </div>
                """, unsafe_allow_html=True)

            with h2:
                st.markdown(f"""
                <div class='metric-card' style='text-align:center;'>
                    <div style='font-size:0.75rem; text-transform:uppercase;
                                letter-spacing:0.08em; color:#999;'>Burnout Score</div>
                    <div style='font-family:Syne,sans-serif; font-size:3.5rem;
                                font-weight:800; color:{score_color(score)};
                                line-height:1.1;'>{score}</div>
                    <div style='font-size:0.75rem; color:#bbb;'>/ 100</div>
                    <div style='font-size:0.72rem; color:#aaa; margin-top:6px;'>
                        Based on {r['CONFIDENCE']} days of data<br>
                        Updated {r['UPDATED_AT'] or 'never'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading student info: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Weekly averages panel ────────────────────────────────────────────────
    st.markdown("### Last 7 Days — Wellness Summary")
    try:
        avg_df = get_df("""
            SELECT
                ROUND(NVL((SELECT AVG(Study_Hours) FROM Study_Logs
                           WHERE Student_ID=:1 AND Log_Date>=SYSDATE-7), 0), 1) AS avg_study,
                ROUND(NVL((SELECT AVG(Sleep_Hours) FROM Sleep_Logs
                           WHERE Student_ID=:1 AND Sleep_Date>=SYSDATE-7), 0), 1) AS avg_sleep,
                ROUND(NVL((SELECT AVG(Mood_Rating) FROM Mood_Tracker
                           WHERE Student_ID=:1 AND Mood_Date>=SYSDATE-7), 0), 1) AS avg_mood,
                ROUND(NVL((SELECT AVG(Stress_Level) FROM Mood_Tracker
                           WHERE Student_ID=:1 AND Mood_Date>=SYSDATE-7), 0), 1) AS avg_stress,
                ROUND(NVL((SELECT SUM(Hours_Spent) FROM Extracurricular_Logs
                           WHERE Student_ID=:1 AND Activity_Date>=SYSDATE-7), 0), 1) AS total_extra
            FROM DUAL
        """, [student_id, student_id, student_id, student_id, student_id])

        if not avg_df.empty:
            av = avg_df.iloc[0]
            m1, m2, m3, m4, m5 = st.columns(5)
            metrics = [
                (m1, "Avg Study",  f"{av['AVG_STUDY']} hrs",
                 "🔴 Overload" if float(av['AVG_STUDY']) > 7 else "🟢 Normal",
                 score_color(float(av['AVG_STUDY']) * 10)),
                (m2, "Avg Sleep",  f"{av['AVG_SLEEP']} hrs",
                 "🔴 Low" if float(av['AVG_SLEEP']) < 6 else "🟢 OK",
                 "#059669" if float(av['AVG_SLEEP']) >= 7 else "#dc2626"),
                (m3, "Avg Mood",   f"{av['AVG_MOOD']} / 10",
                 "🔴 Low" if float(av['AVG_MOOD']) < 5 else "🟢 Good",
                 score_color(float(av['AVG_MOOD']) * 10)),
                (m4, "Avg Stress", f"{av['AVG_STRESS']} / 10",
                 "🔴 High" if float(av['AVG_STRESS']) > 7 else "🟢 Managed",
                 score_color(float(av['AVG_STRESS']) * 10)),
                (m5, "Extra Load", f"{av['TOTAL_EXTRA']} hrs",
                 "⚠️ High" if float(av['TOTAL_EXTRA']) > 10 else "🟢 OK",
                 "#d97706" if float(av['TOTAL_EXTRA']) > 10 else "#059669"),
            ]
            for col, label, val, flag, clr in metrics:
                with col:
                    st.markdown(f"""
                    <div class='metric-card' style='text-align:center; padding:1rem;'>
                        <div style='font-size:0.7rem; text-transform:uppercase;
                                    letter-spacing:0.07em; color:#999;'>{label}</div>
                        <div style='font-family:Syne,sans-serif; font-size:1.5rem;
                                    font-weight:800; color:{clr};'>{val}</div>
                        <div style='font-size:0.72rem; color:#aaa;'>{flag}</div>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load averages: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Enrolled courses ─────────────────────────────────────────────────────
    st.markdown("### Enrolled Courses")
    try:
        courses_df = get_df("""
            SELECT c.Course_Name, c.Credit_Value, c.Difficulty_Level,
                   ROUND(NVL(SUM(sl.Study_Hours),0),1) AS Total_Study_Hrs
            FROM Enrollments e
            JOIN Course_Load c ON e.Course_ID = c.Course_ID
            LEFT JOIN Study_Logs sl
                   ON sl.Course_ID = c.Course_ID
                  AND sl.Student_ID = e.Student_ID
                  AND sl.Log_Date >= SYSDATE - 30
            WHERE e.Student_ID = :1
            GROUP BY c.Course_Name, c.Credit_Value, c.Difficulty_Level
            ORDER BY c.Credit_Value DESC
        """, [student_id])

        if courses_df.empty:
            st.caption("No enrolled courses found.")
        else:
            diff_color = {"Easy": "#059669", "Moderate": "#d97706", "Hard": "#dc2626"}
            for _, cr in courses_df.iterrows():
                dc = diff_color.get(cr["DIFFICULTY_LEVEL"], "#999")
                st.markdown(f"""
                <div class='metric-card' style='padding:0.8rem 1.2rem;
                            display:flex; justify-content:space-between;'>
                    <span style='font-weight:500;'>{cr['COURSE_NAME']}</span>
                    <span style='display:flex; gap:16px; font-size:0.82rem; color:#666;'>
                        <span>{cr['CREDIT_VALUE']} credits</span>
                        <span style='color:{dc}; font-weight:600;'>
                            {cr['DIFFICULTY_LEVEL']}</span>
                        <span>{cr['TOTAL_STUDY_HRS']} hrs studied (30d)</span>
                    </span>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load courses: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Daily trend charts side by side ─────────────────────────────────────
    st.markdown("### 7-Day Trend Charts")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Sleep vs Study Hours**")
        try:
            trend_df = get_df("""
                SELECT TO_CHAR(d.dt,'DD-Mon') AS Day,
                       NVL((SELECT Study_Hours FROM Study_Logs
                            WHERE Student_ID=:1
                              AND Log_Date=d.dt
                              AND ROWNUM=1), 0) AS Study,
                       NVL((SELECT Sleep_Hours FROM Sleep_Logs
                            WHERE Student_ID=:1
                              AND Sleep_Date=d.dt), 0) AS Sleep
                FROM (
                    SELECT TRUNC(SYSDATE) - (LEVEL-1) AS dt
                    FROM DUAL CONNECT BY LEVEL <= 7
                ) d
                ORDER BY d.dt
            """, [student_id, student_id])
            if not trend_df.empty:
                st.line_chart(trend_df.set_index("DAY")[["STUDY", "SLEEP"]])
        except Exception as e:
            st.caption(f"Chart error: {e}")

    with chart_col2:
        st.markdown("**Mood & Stress Levels**")
        try:
            mood_df = get_df("""
                SELECT TO_CHAR(Mood_Date,'DD-Mon') AS Day,
                       Mood_Rating AS Mood,
                       Stress_Level AS Stress
                FROM Mood_Tracker
                WHERE Student_ID = :1
                  AND Mood_Date >= SYSDATE - 7
                ORDER BY Mood_Date
            """, [student_id])
            if mood_df.empty:
                st.caption("No mood data for the past 7 days.")
            else:
                st.line_chart(mood_df.set_index("DAY")[["MOOD", "STRESS"]])
        except Exception as e:
            st.caption(f"Chart error: {e}")

    # ── Alert history ────────────────────────────────────────────────────────
    st.markdown("<br><h3>Recent Alerts</h3>", unsafe_allow_html=True)
    try:
        alerts_df = get_df("""
            SELECT Alert_Type,
                   ROUND(Triggered_Score,1)          AS Score,
                   NVL(Intervention,'—')             AS Intervention,
                   TO_CHAR(Created_At,'DD-Mon HH24:MI') AS Time
            FROM Alerts
            WHERE Student_ID = :1
            ORDER BY Created_At DESC
            FETCH FIRST 5 ROWS ONLY
        """, [student_id])

        if alerts_df.empty:
            st.caption("No alerts generated for this student.")
        else:
            st.dataframe(alerts_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.caption(f"Could not load alerts: {e}")