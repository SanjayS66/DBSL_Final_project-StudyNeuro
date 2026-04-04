import streamlit as st
from datetime import date
from db import get_df, run_dml


# ── Helper: load students ────────────────────────────────────────────────────
def load_students():
    df = get_df("SELECT Student_ID, Name FROM Students ORDER BY Name")
    return {row["NAME"]: row["STUDENT_ID"] for _, row in df.iterrows()}


def load_courses_for(student_id):
    df = get_df("""
        SELECT c.Course_ID, c.Course_Name
        FROM Course_Load c
        JOIN Enrollments e ON c.Course_ID = e.Course_ID
        WHERE e.Student_ID = :1
        ORDER BY c.Course_Name
    """, [student_id])
    return {row["COURSE_NAME"]: row["COURSE_ID"] for _, row in df.iterrows()}


# ── Next sequence value helper (use Oracle sequences) ────────────────────────
def next_id(seq_name: str) -> int:
    from db import run_query
    _, rows = run_query(f"SELECT {seq_name}.NEXTVAL FROM DUAL")
    return rows[0][0]


def show():
    st.markdown("""
    <h1 style='font-size:2.2rem; margin-bottom:0.2rem;'>Daily Log Entry</h1>
    <p style='color:#888; font-size:0.9rem; margin-bottom:2rem;'>
        Record study, sleep, mood and activity data for any student
    </p>
    """, unsafe_allow_html=True)

    # Student selector
    students = load_students()
    if not students:
        st.warning("No students found in the database.")
        return

    sel_col, info_col = st.columns([2, 3])
    with sel_col:
        selected_name = st.selectbox("Select Student", list(students.keys()))
    student_id = students[selected_name]

    # Quick burnout peek
    with info_col:
        from db import get_df as gdf, risk_badge, score_color
        b_df = gdf("""
            SELECT NVL(Risk_Level,'N/A') AS lvl,
                   ROUND(NVL(Calculated_Risk_Score,0),1) AS score
            FROM Burnout_Index WHERE Student_ID = :1
        """, [student_id])
        if not b_df.empty:
            lvl   = b_df["LVL"].iloc[0]
            score = b_df["SCORE"].iloc[0]
            st.markdown(f"""
            <div style='margin-top:1.6rem; padding:0.7rem 1rem;
                        background:#fff; border:1px solid #e8e5de;
                        border-radius:10px; display:inline-block;'>
                <span style='font-size:0.75rem; color:#999;
                             letter-spacing:0.06em; text-transform:uppercase;'>
                    Current Burnout Score
                </span>
                &nbsp;
                <span style='font-family:Syne,sans-serif; font-weight:800;
                             font-size:1.2rem; color:{score_color(score)};'>{score}</span>
                &nbsp;
                {risk_badge(lvl)}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

    tab_sleep, tab_study, tab_mood, tab_extra = st.tabs([
        "😴  Sleep", "📚  Study", "😊  Mood & Stress", "🏃  Extracurricular"
    ])

    # ── SLEEP LOG ────────────────────────────────────────────────────────────
    with tab_sleep:
        st.markdown("#### Log Sleep Entry")
        c1, c2, c3 = st.columns(3)
        with c1:
            sleep_date = st.date_input("Date", value=date.today(), key="sl_date")
        with c2:
            sleep_hours = st.slider("Hours Slept", 0.0, 12.0, 7.0, 0.5, key="sl_hrs")
        with c3:
            sleep_qual = st.selectbox("Sleep Quality",
                                      ["Poor", "Fair", "Good", "Excellent"], key="sl_q")

        if st.button("💾  Save Sleep Log", key="save_sleep"):
            try:
                # FIX: Corrected sequence name to match your SQL schema
                new_id = next_id("SleepLog_Seq") 
                run_dml("""
                    INSERT INTO Sleep_Logs
                        (Sleep_ID, Student_ID, Sleep_Date, Sleep_Hours, Sleep_Quality)
                    VALUES (:1, :2, TO_DATE(:3,'YYYY-MM-DD'), :4, :5)
                """, [new_id, student_id, str(sleep_date), sleep_hours, sleep_qual])
                st.success("✅ Sleep log saved!")
            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown("##### Recent Entries (last 7 days)")
        try:
            # FIX: Changed alias 'Date' to 'Log_Date' to avoid ORA-00923
            sl_df = get_df("""
                SELECT TO_CHAR(Sleep_Date,'DD-Mon-YYYY') AS Log_Date,
                       Sleep_Hours AS Hours,
                       NVL(Sleep_Quality,'—') AS Quality
                FROM Sleep_Logs
                WHERE Student_ID = :1
                  AND Sleep_Date >= SYSDATE - 7
                ORDER BY Sleep_Date DESC
            """, [student_id])
            if sl_df.empty:
                st.caption("No sleep logs for the past 7 days.")
            else:
                st.dataframe(sl_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Could not load logs: {e}")

    # ── STUDY LOG ────────────────────────────────────────────────────────────
    with tab_study:
        st.markdown("#### Log Study Session")
        courses = load_courses_for(student_id)
        if not courses:
            st.info("This student has no enrolled courses.")
        else:
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                sel_course = st.selectbox("Course", list(courses.keys()), key="st_course")
            with sc2:
                study_date = st.date_input("Date", value=date.today(), key="st_date")
            with sc3:
                study_hours = st.slider("Hours Studied", 0.0, 16.0, 2.0, 0.5, key="st_hrs")

            if st.button("💾  Save Study Log", key="save_study"):
                try:
                    # FIX: Corrected sequence name
                    new_id = next_id("StudyLog_Seq")
                    run_dml("""
                        INSERT INTO Study_Logs
                            (Log_ID, Student_ID, Course_ID, Log_Date, Study_Hours)
                        VALUES (:1, :2, :3, TO_DATE(:4,'YYYY-MM-DD'), :5)
                    """, [new_id, student_id, courses[sel_course], str(study_date), study_hours])
                    st.success("✅ Study log saved!")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── MOOD LOG ─────────────────────────────────────────────────────────────
    with tab_mood:
        st.markdown("#### Log Mood & Stress")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            mood_date = st.date_input("Date", value=date.today(), key="mo_date")
        with mc2:
            mood_rating = st.slider("Mood (1 = very low, 10 = great)", 1, 10, 7, key="mo_mood")
        with mc3:
            stress_lvl = st.slider("Stress (1 = calm, 10 = overwhelmed)", 1, 10, 3, key="mo_stress")

        mood_emojis = {1:"😢",2:"😢",3:"😟",4:"😕",5:"😐",
                       6:"🙂",7:"😊",8:"😄",9:"🤩",10:"🤩"}
        stress_emojis = {1:"😌",2:"😌",3:"🙂",4:"🙂",5:"😐",
                         6:"😬",7:"😰",8:"😱",9:"🤯",10:"🤯"}

        st.markdown(f"""
        <div style='display:flex; gap:2rem; margin:1rem 0;'>
            <div style='text-align:center;'>
                <div style='font-size:2.5rem;'>{mood_emojis[mood_rating]}</div>
                <div style='font-size:0.8rem; color:#888;'>Mood</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:2.5rem;'>{stress_emojis[stress_lvl]}</div>
                <div style='font-size:0.8rem; color:#888;'>Stress</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾  Save Mood Log", key="save_mood"):
            try:
                new_id = next_id("Mood_Seq")
                run_dml("""
                    INSERT INTO Mood_Tracker
                        (Mood_ID, Student_ID, Mood_Date, Mood_Rating, Stress_Level)
                    VALUES (:1, :2, TO_DATE(:3,'YYYY-MM-DD'), :4, :5)
                """, [new_id, student_id, str(mood_date), mood_rating, stress_lvl])
                st.success("✅ Mood logged! Burnout score recalculated.")
            except Exception as e:
                if "ORA-00001" in str(e):
                    st.warning("A mood entry already exists for this date.")
                else:
                    st.error(f"Error: {e}")

        st.markdown("##### Mood & Stress Trend (last 7 days)")
        try:
            trend_df = get_df("""
                SELECT TO_CHAR(Mood_Date,'DD-Mon') AS Day,
                       Mood_Rating AS Mood,
                       Stress_Level AS Stress
                FROM Mood_Tracker
                WHERE Student_ID = :1
                  AND Mood_Date >= SYSDATE - 7
                ORDER BY Mood_Date ASC
            """, [student_id])
            if trend_df.empty:
                st.caption("No mood data for the past 7 days.")
            else:
                st.line_chart(trend_df.set_index("DAY")[["MOOD", "STRESS"]])
        except Exception as e:
            st.caption(f"Could not load trend: {e}")

    # ── EXTRACURRICULAR LOG ──────────────────────────────────────────────────
    with tab_extra:
        st.markdown("#### Log Extracurricular Activity")
        ec1, ec2 = st.columns(2)
        with ec1:
            activity_name = st.text_input("Activity Name",
                                          placeholder="e.g. Football Practice", key="ex_name")
            category = st.selectbox("Category",
                                    ["Sports","Club","Cultural","Volunteering","Other"], key="ex_cat")
        with ec2:
            act_date    = st.date_input("Date", value=date.today(), key="ex_date")
            act_hours   = st.slider("Hours Spent", 0.0, 8.0, 1.0, 0.5, key="ex_hrs")

        if st.button("💾  Save Activity Log", key="save_extra"):
            if not activity_name.strip():
                st.warning("Please enter an activity name.")
            else:
                try:
                    new_id = next_id("Extra_Log_Seq")
                    run_dml("""
                        INSERT INTO Extracurricular_Logs
                            (Activity_ID, Student_ID, Activity_Name,
                             Category, Activity_Date, Hours_Spent)
                        VALUES (:1, :2, :3, :4, TO_DATE(:5,'YYYY-MM-DD'), :6)
                    """, [new_id, student_id, activity_name.strip(),
                          category, str(act_date), act_hours])
                    st.success("✅ Activity logged!")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("##### Activity Breakdown This Week")
        try:
            ex_df = get_df("""
                SELECT Category, ROUND(SUM(Hours_Spent),1) AS Hours
                FROM Extracurricular_Logs
                WHERE Student_ID = :1
                  AND Activity_Date >= SYSDATE - 7
                GROUP BY Category
                ORDER BY Hours DESC
            """, [student_id])
            if ex_df.empty:
                st.caption("No activity logs this week.")
            else:
                st.bar_chart(ex_df.set_index("CATEGORY")["HOURS"])
        except Exception as e:
            st.caption(f"Could not load chart: {e}")