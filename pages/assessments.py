import streamlit as st
from datetime import date, timedelta
from db import get_df, run_dml, run_query


def show():
    st.markdown("""
    <h1 style='font-size:2.2rem; margin-bottom:0.2rem;'>Assessment Schedule</h1>
    <p style='color:#888; font-size:0.9rem; margin-bottom:2rem;'>
        Upcoming exams, quizzes and assignments — correlated with student stress
    </p>
    """, unsafe_allow_html=True)

    tab_view, tab_add, tab_correlate = st.tabs([
        "📅  Upcoming", "➕  Add Assessment", "🔗  Stress Correlation"
    ])

# ── UPCOMING ASSESSMENTS ─────────────────────────────────────────────────
    with tab_view:
        st.markdown("#### Assessments in the Next 30 Days")
        
        # FIX: Changed alias 'Date' to 'Exam_Date' to avoid Oracle Reserved Word conflict
        # FIX: Ensure column selection matches the keys used in the UI loop
        query_upcoming = """
            SELECT 
                a.Assessment_ID,
                c.Course_Name,
                a.Assessment_Type,
                TO_CHAR(a.Assessment_Date, 'DD-Mon-YYYY') AS Exam_Date,
                a.Weightage                              AS Weightage_Pct,
                TRUNC(a.Assessment_Date - SYSDATE)       AS Days_Away
            FROM Assessments_Schedule a
            JOIN Course_Load c ON a.Course_ID = c.Course_ID
            WHERE a.Assessment_Date BETWEEN SYSDATE AND SYSDATE + 30
            ORDER BY a.Assessment_Date ASC
        """
        
        try:
            upcoming_df = get_df(query_upcoming)

            if upcoming_df.empty:
                st.info("No assessments scheduled in the next 30 days.")
            else:
                type_colors = {
                    "End-Sem":    ("#fee2e2", "#991b1b"),
                    "Mid-Sem":    ("#fef3c7", "#92400e"),
                    "Quiz":       ("#dbeafe", "#1e40af"),
                    "Assignment": ("#d1fae5", "#065f46"),
                }

                for _, row in upcoming_df.iterrows():
                    # NOTE: Oracle/Pandas usually returns columns in UPPERCASE
                    a_type = row.get("ASSESSMENT_TYPE", "Other")
                    course = row.get("COURSE_NAME", "Unknown Course")
                    e_date = row.get("EXAM_DATE", "N/A")
                    weight = row.get("WEIGHTAGE_PCT", 0)
                    days_raw = row.get("DAYS_AWAY")
                    
                    bg, fg = type_colors.get(a_type, ("#f3f4f6", "#374151"))
                    
                    # Logic for Urgency
                    days = int(days_raw) if days_raw is not None else 0
                    if days <= 3:
                        urgency, icon = "Imminent", "🔴"
                    elif days <= 7:
                        urgency, icon = "This Week", "🟠"
                    else:
                        urgency, icon = "Upcoming", "🟢"

                    st.markdown(f"""
                    <div class='metric-card' style='padding:0.9rem 1.3rem; border-left:4px solid {fg};'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div>
                                <span style='font-family:Syne,sans-serif; font-weight:700; color:#1a1a1a;'>{course}</span>
                                &nbsp;
                                <span style='background:{bg}; color:{fg}; padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:600;'>
                                    {a_type}
                                </span>
                            </div>
                            <div style='text-align:right; font-size:0.83rem; color:#666;'>
                                <div><b>{e_date}</b> &nbsp;·&nbsp; {weight}% weightage</div>
                                <div style='margin-top:2px;'>{icon} {urgency} — {days} days away</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error loading upcoming assessments: {e}")

        # ── ALL ASSESSMENTS TABLE ────────────────────────────────────────────
        st.markdown("<br><h4>All Scheduled Assessments</h4>", unsafe_allow_html=True)
        query_all = """
            SELECT 
                c.Course_Name        AS Course,
                a.Assessment_Type    AS Type,
                TO_CHAR(a.Assessment_Date, 'DD-Mon-YYYY') AS Exam_Date,
                a.Weightage          AS Weight_Pct
            FROM Assessments_Schedule a
            JOIN Course_Load c ON a.Course_ID = c.Course_ID
            ORDER BY a.Assessment_Date DESC
        """
        try:
            all_df = get_df(query_all)
            if not all_df.empty:
                st.dataframe(all_df, use_container_width=True, hide_index=True)
            else:
                st.caption("No historical or future assessments found in the database.")
        except Exception as e:
            st.error(f"Could not load full schedule: {e}")

    # ── ADD ASSESSMENT ───────────────────────────────────────────────────────
    with tab_add:
        st.markdown("#### Schedule a New Assessment")

        try:
            courses_df = get_df(
                "SELECT Course_ID, Course_Name FROM Course_Load ORDER BY Course_Name"
            )
            course_map = {r["COURSE_NAME"]: r["COURSE_ID"]
                          for _, r in courses_df.iterrows()}
        except Exception as e:
            st.error(f"Could not load courses: {e}")
            return

        ac1, ac2 = st.columns(2)
        with ac1:
            sel_course = st.selectbox("Course", list(course_map.keys()), key="as_course")
            assess_type = st.selectbox("Type",
                ["Quiz", "Mid-Sem", "End-Sem", "Assignment"], key="as_type")
        with ac2:
            assess_date = st.date_input("Date",
                value=date.today() + timedelta(days=7), key="as_date")
            weightage = st.number_input("Weightage (%)", 1.0, 100.0, 20.0,
                                        step=5.0, key="as_weight")

        if st.button("➕  Add Assessment", key="save_assess"):
            try:
                _, rows = run_query("SELECT Assess_Seq.NEXTVAL FROM DUAL")
                new_id = rows[0][0]
                run_dml("""
                    INSERT INTO Assessments_Schedule
                        (Assessment_ID, Course_ID, Assessment_Type,
                         Assessment_Date, Weightage)
                    VALUES (:1, :2, :3, TO_DATE(:4,'YYYY-MM-DD'), :5)
                """, [new_id, course_map[sel_course], assess_type,
                      str(assess_date), weightage])
                st.success(f"✅ {assess_type} for {sel_course} scheduled on {assess_date}!")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── STRESS CORRELATION ───────────────────────────────────────────────────
    with tab_correlate:
        st.markdown("#### Pre-Exam Stress Pattern")
        st.markdown("""
        <p style='color:#888; font-size:0.85rem;'>
            This query joins Mood_Tracker with Assessments_Schedule to show
            whether student stress levels spike in the days before an exam.
        </p>
        """, unsafe_allow_html=True)

        try:
            corr_df = get_df("""
                SELECT
                    c.Course_Name,
                    a.Assessment_Type,
                    TO_CHAR(a.Assessment_Date,'DD-Mon-YYYY')   AS Exam_Date,
                    ROUND(AVG(mt.Stress_Level), 1)             AS Avg_Stress_Before,
                    ROUND(AVG(mt.Mood_Rating),  1)             AS Avg_Mood_Before,
                    COUNT(DISTINCT mt.Student_ID)              AS Students_Logged
                FROM Assessments_Schedule a
                JOIN Course_Load c ON a.Course_ID = c.Course_ID
                JOIN Enrollments  e ON e.Course_ID = a.Course_ID
                JOIN Mood_Tracker mt
                    ON  mt.Student_ID = e.Student_ID
                    AND mt.Mood_Date BETWEEN a.Assessment_Date - 7
                                        AND a.Assessment_Date
                GROUP BY c.Course_Name, a.Assessment_Type, a.Assessment_Date
                ORDER BY a.Assessment_Date DESC
            """)

            if corr_df.empty:
                st.info("Not enough data yet. Log more mood entries near assessment dates.")
            else:
                st.dataframe(corr_df, use_container_width=True, hide_index=True)

                # Visualise avg stress per assessment
                if len(corr_df) > 1:
                    label = corr_df["COURSE_NAME"] + " — " + corr_df["ASSESSMENT_TYPE"]
                    corr_df["LABEL"] = label
                    st.bar_chart(corr_df.set_index("LABEL")["AVG_STRESS_BEFORE"])
        except Exception as e:
            st.warning(f"Correlation query failed: {e}")