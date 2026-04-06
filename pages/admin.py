import streamlit as st
from datetime import date
from db import get_df, run_dml, run_query, call_procedure


def show():
    st.markdown("""
    <h1 style='font-size:2.2rem; margin-bottom:0.2rem;'>Admin Panel</h1>
    <p style='color:#888; font-size:0.9rem; margin-bottom:2rem;'>
        Manage students, courses, enrollments and run PL/SQL utilities
    </p>
    """, unsafe_allow_html=True)

    tab_students, tab_courses, tab_enroll, tab_plsql = st.tabs([
        "👤  Students", "📚  Courses", "🔗  Enrollments", "⚙️  PL/SQL Utilities"
    ])

    # ── STUDENTS ─────────────────────────────────────────────────────────────
    with tab_students:
        st.markdown("#### Add New Student")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            new_name = st.text_input("Full Name", key="ns_name")
        with sc2:
            try:
                br_df = get_df("SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name")
                br_map = {r["BRANCH_NAME"]: r["BRANCH_ID"] for _, r in br_df.iterrows()}
                sel_br = st.selectbox("Branch", list(br_map.keys()), key="ns_branch")
            except Exception:
                br_map = {}
                sel_br = None
        with sc3:
            year = st.selectbox("Year of Study", [1, 2, 3, 4], index=1, key="ns_year")

        join_date = st.date_input("Date of Joining", value=date.today(), key="ns_join")

        if st.button("➕  Add Student", key="add_student"):
            if not new_name.strip():
                st.warning("Please enter a student name.")
            elif not br_map:
                st.warning("No branches found in database.")
            else:
                try:
                    _, rows = run_query("SELECT Student_Seq.NEXTVAL FROM DUAL")
                    new_id = rows[0][0]
                    run_dml("""
                        INSERT INTO Students
                            (Student_ID, Name, Branch_ID, Year_of_Study, Date_of_Joining)
                        VALUES (:1, :2, :3, :4, TO_DATE(:5,'YYYY-MM-DD'))
                    """, [new_id, new_name.strip(), br_map[sel_br], year, str(join_date)])
                    st.success(f"✅ Student '{new_name}' added with ID {new_id}.")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("<br><h4>All Students</h4>", unsafe_allow_html=True)
        try:
            s_df = get_df("""
                SELECT s.Student_ID AS ID, s.Name,
                       br.Branch_Name AS Branch,
                       s.Year_of_Study AS Year,
                       TO_CHAR(s.Date_of_Joining,'DD-Mon-YYYY') AS Joined,
                       NVL(b.Risk_Level,'N/A') AS Risk
                FROM Students s
                JOIN Branches br ON s.Branch_ID = br.Branch_ID
                LEFT JOIN Burnout_Index b ON s.Student_ID = b.Student_ID
                ORDER BY s.Student_ID
            """)
            st.dataframe(s_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error loading students: {e}")

    # ── COURSES ───────────────────────────────────────────────────────────────
    with tab_courses:
        st.markdown("#### Add New Course")
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            course_name = st.text_input("Course Name", key="nc_name")
        with cc2:
            credits = st.number_input("Credits", 1, 6, 3, key="nc_credits")
        with cc3:
            difficulty = st.selectbox("Difficulty", ["Easy","Moderate","Hard"], key="nc_diff")

        if st.button("➕  Add Course", key="add_course"):
            if not course_name.strip():
                st.warning("Please enter a course name.")
            else:
                try:
                    _, rows = run_query("SELECT Course_Seq.NEXTVAL FROM DUAL")
                    new_id = rows[0][0]
                    run_dml("""
                        INSERT INTO Course_Load
                            (Course_ID, Course_Name, Credit_Value, Difficulty_Level)
                        VALUES (:1, :2, :3, :4)
                    """, [new_id, course_name.strip(), credits, difficulty])
                    st.success(f"✅ Course '{course_name}' added.")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("<br><h4>All Courses</h4>", unsafe_allow_html=True)
        try:
            c_df = get_df("""
                SELECT Course_ID AS ID, Course_Name AS Name,
                       Credit_Value AS Credits, Difficulty_Level AS Difficulty
                FROM Course_Load ORDER BY Course_ID
            """)
            st.dataframe(c_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error loading courses: {e}")

    # ── ENROLLMENTS ──────────────────────────────────────────────────────────
    with tab_enroll:
        st.markdown("#### Enroll a Student in a Course")
        try:
            s_df2 = get_df("SELECT Student_ID, Name FROM Students ORDER BY Name")
            s_map2 = {r["NAME"]: r["STUDENT_ID"] for _, r in s_df2.iterrows()}
            c_df2  = get_df("SELECT Course_ID, Course_Name FROM Course_Load ORDER BY Course_Name")
            c_map2 = {r["COURSE_NAME"]: r["COURSE_ID"] for _, r in c_df2.iterrows()}
            sem_df = get_df("SELECT Semester_ID, Semester_Name FROM Semesters ORDER BY Semester_ID")
            sem_map = {r["SEMESTER_NAME"]: r["SEMESTER_ID"] for _, r in sem_df.iterrows()}
        except Exception as e:
            st.error(f"Could not load data: {e}")
            return

        en1, en2, en3 = st.columns(3)
        with en1: sel_s2  = st.selectbox("Student", list(s_map2.keys()), key="en_student")
        with en2: sel_c2  = st.selectbox("Course",  list(c_map2.keys()), key="en_course")
        with en3: sel_sem = st.selectbox("Semester", list(sem_map.keys()), key="en_sem")

        if st.button("🔗  Enroll", key="do_enroll"):
            try:
                _, rows = run_query("SELECT Enroll_Seq.NEXTVAL FROM DUAL")
                new_id = rows[0][0]
                run_dml("""
                    INSERT INTO Enrollments
                        (Enrollment_ID, Student_ID, Course_ID, Semester_ID)
                    VALUES (:1, :2, :3, :4)
                """, [new_id, s_map2[sel_s2], c_map2[sel_c2], sem_map[sel_sem]])
                st.success(f"✅ {sel_s2} enrolled in {sel_c2}.")
            except Exception as e:
                if "ORA-00001" in str(e):
                    st.warning("This student is already enrolled in this course for the selected semester.")
                else:
                    st.error(f"Error: {e}")

        st.markdown("<br><h4>Enrollment Overview</h4>", unsafe_allow_html=True)
        try:
            enroll_df = get_df("""
                SELECT s.Name AS Student,
                       c.Course_Name AS Course,
                       sem.Semester_Name AS Semester,
                       c.Credit_Value AS Credits
                FROM Enrollments e
                JOIN Students s    ON e.Student_ID  = s.Student_ID
                JOIN Course_Load c ON e.Course_ID   = c.Course_ID
                JOIN Semesters sem ON e.Semester_ID = sem.Semester_ID
                ORDER BY s.Name, c.Course_Name
            """)
            st.dataframe(enroll_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error: {e}")

    # ── PL/SQL UTILITIES ─────────────────────────────────────────────────────
    with tab_plsql:
        st.markdown("#### Run PL/SQL Package Procedures")
        st.markdown("""
        <p style='color:#888; font-size:0.85rem; margin-bottom:1rem;'>
            These buttons invoke stored procedures and functions defined in
            <code>Wellness_Pkg</code> and standalone Oracle objects.
        </p>
        """, unsafe_allow_html=True)

        # Refresh all
        st.markdown("**Wellness_Pkg.Refresh_All_Students**")
        st.caption("Loops through every student and recalculates their burnout score using the stored function.")
        if st.button("▶️  Run Refresh_All_Students", key="run_refresh_all"):
            with st.spinner("Running PL/SQL procedure…"):
                try:
                    call_procedure("Wellness_Pkg.Refresh_All_Students")
                    st.success("✅ All burnout scores refreshed.")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)

        # Print report for one student (calls package procedure)
        st.markdown("**Wellness_Pkg.Print_Wellness_Report**")
        st.caption("Executes the package procedure for a single student and shows DBMS_OUTPUT.")
        try:
            s_df3 = get_df("SELECT Student_ID, Name FROM Students ORDER BY Name")
            s_map3 = {r["NAME"]: r["STUDENT_ID"] for _, r in s_df3.iterrows()}
            sel_s3 = st.selectbox("Select student", list(s_map3.keys()), key="plsql_student")
        except Exception:
            s_map3 = {}
            sel_s3 = None

        if st.button("▶️  Run Print_Wellness_Report", key="run_report"):
            if not s_map3 or not sel_s3:
                st.warning("No students available.")
            else:
                try:
                    # Fetch the summary directly as a query instead of DBMS_OUTPUT
                    sid = s_map3[sel_s3]
                    call_procedure("Refresh_Burnout_Index", [sid])
                    report_df = get_df("""
                        SELECT
                            s.Name,
                            ROUND(NVL(b.Calculated_Risk_Score,0),1) AS Score,
                            NVL(b.Risk_Level,'N/A')                  AS Risk,
                            NVL(b.Confidence_Score,0)               AS Data_Days,
                            ROUND(NVL((SELECT AVG(Sleep_Hours) FROM Sleep_Logs
                                WHERE Student_ID=s.Student_ID AND Sleep_Date>=SYSDATE-7),0),1) AS Avg_Sleep,
                            ROUND(NVL((SELECT AVG(Study_Hours) FROM Study_Logs
                                WHERE Student_ID=s.Student_ID AND Log_Date>=SYSDATE-7),0),1)  AS Avg_Study,
                            ROUND(NVL((SELECT AVG(Mood_Rating) FROM Mood_Tracker
                                WHERE Student_ID=s.Student_ID AND Mood_Date>=SYSDATE-7),0),1) AS Avg_Mood
                        FROM Students s
                        LEFT JOIN Burnout_Index b ON s.Student_ID = b.Student_ID
                        WHERE s.Student_ID = :1
                    """, [sid])
                    if not report_df.empty:
                        r = report_df.iloc[0]
                        from db import risk_badge, score_color
                        st.markdown(f"""
                        <div class='metric-card' style='font-family:monospace;
                                    font-size:0.88rem; line-height:2;'>
                            <div style='font-family:Syne,sans-serif; font-weight:700;
                                        font-size:1.1rem; margin-bottom:8px;'>
                                Wellness Report — {r['NAME']}
                            </div>
                            <div>Burnout Score &nbsp;&nbsp;:
                                <strong style='color:{score_color(r["SCORE"])};'>
                                    {r['SCORE']} / 100
                                </strong>
                            </div>
                            <div>Risk Level &nbsp;&nbsp;&nbsp;&nbsp;: {risk_badge(r['RISK'])}</div>
                            <div>Avg Sleep &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:
                                <strong>{r['AVG_SLEEP']} hrs/day</strong></div>
                            <div>Avg Study &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:
                                <strong>{r['AVG_STUDY']} hrs/day</strong></div>
                            <div>Avg Mood &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:
                                <strong>{r['AVG_MOOD']} / 10</strong></div>
                            <div>Data Days &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:
                                <strong>{r['DATA_DAYS']} days used</strong></div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)

        # Raw SQL console (for demo/evaluation purposes)
        st.markdown("**SQL Console** _(read-only SELECT queries only)_")
        raw_sql = st.text_area("Enter SQL", height=100,
                               placeholder="SELECT * FROM Students",
                               key="raw_sql")
        if st.button("▶️  Execute", key="run_sql"):
            if not raw_sql.strip().upper().startswith("SELECT"):
                st.warning("Only SELECT statements are allowed here.")
            else:
                try:
                    result_df = get_df(raw_sql.strip())
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                    st.caption(f"{len(result_df)} rows returned.")
                except Exception as e:
                    st.error(f"Query error: {e}")