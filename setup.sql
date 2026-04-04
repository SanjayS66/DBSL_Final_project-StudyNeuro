--table creation
CREATE TABLE Branches (
    Branch_ID   NUMBER(5) PRIMARY KEY,
    Branch_Name VARCHAR2(50) NOT NULL UNIQUE,
    HOD_Name    VARCHAR2(100)
);

CREATE TABLE Semesters (
    Semester_ID   NUMBER(3) PRIMARY KEY,
    Semester_Name VARCHAR2(20) NOT NULL,  
    Academic_Year VARCHAR2(10) NOT NULL   
);

CREATE TABLE Students (
    Student_ID      NUMBER(6)    PRIMARY KEY,
    Name            VARCHAR2(100) NOT NULL,
    Branch_ID       NUMBER(5)    NOT NULL,
    Year_of_Study   NUMBER(1)    NOT NULL CHECK (Year_of_Study BETWEEN 1 AND 4),
    Date_of_Joining DATE         NOT NULL,
    CONSTRAINT fk_student_branch FOREIGN KEY (Branch_ID) REFERENCES Branches(Branch_ID)
);

CREATE TABLE Course_Load (
    Course_ID        NUMBER(6)    PRIMARY KEY,
    Course_Name      VARCHAR2(100) NOT NULL,
    Credit_Value     NUMBER(2)    NOT NULL CHECK (Credit_Value BETWEEN 1 AND 6),
    Difficulty_Level VARCHAR2(10) NOT NULL
        CHECK (Difficulty_Level IN ('Easy', 'Moderate', 'Hard'))
);

CREATE TABLE Enrollments (
    Enrollment_ID   NUMBER(8)  PRIMARY KEY,
    Student_ID      NUMBER(6)  NOT NULL,
    Course_ID       NUMBER(6)  NOT NULL,
    Semester_ID     NUMBER(3)  NOT NULL,
    CONSTRAINT fk_enroll_student  FOREIGN KEY (Student_ID)  REFERENCES Students(Student_ID),
    CONSTRAINT fk_enroll_course   FOREIGN KEY (Course_ID)   REFERENCES Course_Load(Course_ID),
    CONSTRAINT fk_enroll_semester FOREIGN KEY (Semester_ID) REFERENCES Semesters(Semester_ID),
    CONSTRAINT uq_enrollment UNIQUE (Student_ID, Course_ID, Semester_ID)
);

CREATE TABLE Assessments_Schedule (
    Assessment_ID   NUMBER(8)    PRIMARY KEY,
    Course_ID       NUMBER(6)    NOT NULL,
    Assessment_Type VARCHAR2(30) NOT NULL CHECK (Assessment_Type IN ('Quiz','Mid-Sem','End-Sem','Assignment')),
    Assessment_Date DATE         NOT NULL,
    Weightage       NUMBER(5,2)  NOT NULL CHECK (Weightage BETWEEN 0 AND 100),
    CONSTRAINT fk_assess_course FOREIGN KEY (Course_ID) REFERENCES Course_Load(Course_ID)
);

CREATE TABLE Study_Logs (
    Log_ID          NUMBER(10)  PRIMARY KEY,
    Student_ID      NUMBER(6)   NOT NULL,
    Course_ID       NUMBER(6)   NOT NULL,
    Assessment_ID   NUMBER(8),  
    Log_Date        DATE        NOT NULL,
    Study_Hours     NUMBER(4,2) NOT NULL CHECK (Study_Hours > 0 AND Study_Hours <= 24),
    CONSTRAINT fk_studylog_student    FOREIGN KEY (Student_ID)    REFERENCES Students(Student_ID),
    CONSTRAINT fk_studylog_course     FOREIGN KEY (Course_ID)     REFERENCES Course_Load(Course_ID),
    CONSTRAINT fk_studylog_assess     FOREIGN KEY (Assessment_ID) REFERENCES Assessments_Schedule(Assessment_ID)
);

CREATE TABLE Sleep_Logs (
    Sleep_ID      NUMBER(10)   PRIMARY KEY,
    Student_ID    NUMBER(6)    NOT NULL,
    Sleep_Date    DATE         NOT NULL,
    Sleep_Hours   NUMBER(4,2)  NOT NULL CHECK (Sleep_Hours > 0 AND Sleep_Hours <= 24),
    Sleep_Quality VARCHAR2(10) CHECK (Sleep_Quality IN ('Poor','Fair','Good','Excellent')),
    CONSTRAINT fk_sleeplog_student FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID),
    CONSTRAINT uq_sleep_per_day UNIQUE (Student_ID, Sleep_Date)
);

CREATE TABLE Mood_Tracker (
    Mood_ID       NUMBER(10)  PRIMARY KEY,
    Student_ID    NUMBER(6)   NOT NULL,
    Assessment_ID NUMBER(8),  
    Mood_Date     DATE        NOT NULL,
    Mood_Rating   NUMBER(2)   NOT NULL CHECK (Mood_Rating BETWEEN 1 AND 10),
    Stress_Level  NUMBER(2)   NOT NULL CHECK (Stress_Level BETWEEN 1 AND 10),
    CONSTRAINT fk_mood_student FOREIGN KEY (Student_ID)    REFERENCES Students(Student_ID),
    CONSTRAINT fk_mood_assess  FOREIGN KEY (Assessment_ID) REFERENCES Assessments_Schedule(Assessment_ID),
    CONSTRAINT uq_mood_per_day UNIQUE (Student_ID, Mood_Date)
);

CREATE TABLE Extracurricular_Logs (
    Activity_ID   NUMBER(10)   PRIMARY KEY,
    Student_ID    NUMBER(6)    NOT NULL,
    Activity_Name VARCHAR2(100) NOT NULL,
    Category      VARCHAR2(30) CHECK (Category IN ('Sports','Club','Cultural','Volunteering','Other')),
    Activity_Date DATE         NOT NULL,
    Hours_Spent   NUMBER(4,2)  NOT NULL CHECK (Hours_Spent > 0 AND Hours_Spent <= 24),
    CONSTRAINT fk_extra_student FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID)
);

CREATE TABLE Burnout_Index (
    Burnout_Log_ID       NUMBER(10)   PRIMARY KEY,
    Student_ID           NUMBER(6)    NOT NULL,
    Calculated_Risk_Score NUMBER(5,2),
    Risk_Level           VARCHAR2(10) CHECK (Risk_Level IN ('Low','Moderate','High','Critical')),
    Confidence_Score     NUMBER(3),   
    Calculated_At        TIMESTAMP    DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_burnout_student FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID)
);

CREATE TABLE Alerts (
    Alert_ID        NUMBER(10)    PRIMARY KEY,
    Student_ID      NUMBER(6)     NOT NULL,
    Alert_Type      VARCHAR2(50)  NOT NULL,
    Triggered_Score NUMBER(5,2),
    Intervention    VARCHAR2(300),
    Created_At      TIMESTAMP     DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_alert_student FOREIGN KEY (Student_ID)
        REFERENCES Students(Student_ID)
);


-- sequence creation for insertion counter
CREATE SEQUENCE Branch_Seq    START WITH 1   INCREMENT BY 1;
CREATE SEQUENCE Semester_Seq  START WITH 1   INCREMENT BY 1;
CREATE SEQUENCE Student_Seq   START WITH 1001 INCREMENT BY 1;
CREATE SEQUENCE Course_Seq    START WITH 201  INCREMENT BY 1;
CREATE SEQUENCE Enroll_Seq    START WITH 3001 INCREMENT BY 1;
CREATE SEQUENCE Assess_Seq    START WITH 401  INCREMENT BY 1;
CREATE SEQUENCE StudyLog_Seq  START WITH 5001 INCREMENT BY 1;
CREATE SEQUENCE SleepLog_Seq  START WITH 6001 INCREMENT BY 1;
CREATE SEQUENCE Mood_Seq      START WITH 7001 INCREMENT BY 1;
CREATE SEQUENCE Extra_Seq     START WITH 8001 INCREMENT BY 1;
CREATE SEQUENCE Burnout_Seq   START WITH 9001 INCREMENT BY 1;
CREATE SEQUENCE Alert_Seq     START WITH 10001 INCREMENT BY 1;

SELECT table_name FROM user_tables ORDER BY table_name;

COMMIT;

--insert test values
-- Branches table
INSERT INTO Branches VALUES (Branch_Seq.NEXTVAL, 'Computer Science and Engineering', 'Dr. Arun Sharma');
INSERT INTO Branches VALUES (Branch_Seq.NEXTVAL, 'Electronics and Communication',    'Dr. Meera Rao');
INSERT INTO Branches VALUES (Branch_Seq.NEXTVAL, 'Mechanical Engineering',         'Dr. Suresh Patel');
INSERT INTO Branches VALUES (Branch_Seq.NEXTVAL, 'Information Technology',         'Dr. Kavitha Nair');
select * from Branches;

-- Semesters table
INSERT INTO Semesters VALUES (Semester_Seq.NEXTVAL, '3rd Sem', '2024-25');
INSERT INTO Semesters VALUES (Semester_Seq.NEXTVAL, '4th Sem', '2024-25');
INSERT INTO Semesters VALUES (Semester_Seq.NEXTVAL, '5th Sem', '2024-25');
select * from Semesters;

-- Students table
INSERT INTO Students VALUES (Student_Seq.NEXTVAL, 'Arjun Nair',      1, 2, TO_DATE('01-08-2023','DD-MM-YYYY'));
INSERT INTO Students VALUES (Student_Seq.NEXTVAL, 'Priya Shetty',    1, 2, TO_DATE('01-08-2023','DD-MM-YYYY'));
INSERT INTO Students VALUES (Student_Seq.NEXTVAL, 'Rahul Kamath',    2, 2, TO_DATE('01-08-2023','DD-MM-YYYY'));
INSERT INTO Students VALUES (Student_Seq.NEXTVAL, 'Sneha Bhat',      1, 2, TO_DATE('01-08-2023','DD-MM-YYYY'));
INSERT INTO Students VALUES (Student_Seq.NEXTVAL, 'Vikram Hegde',    3, 2, TO_DATE('01-08-2023','DD-MM-YYYY'));
INSERT INTO Students VALUES (Student_Seq.NEXTVAL, 'Ananya Kulkarni', 4, 2, TO_DATE('01-08-2023','DD-MM-YYYY'));
INSERT INTO Students VALUES (Student_Seq.NEXTVAL, 'Kiran Mallya',    1, 3, TO_DATE('01-08-2022','DD-MM-YYYY'));
INSERT INTO Students VALUES (Student_Seq.NEXTVAL, 'Divya Pai',       2, 3, TO_DATE('01-08-2022','DD-MM-YYYY'));
select * from Students;

-- FK verification
SELECT s.Student_ID, s.Name, b.Branch_Name, s.Year_of_Study
FROM Students s JOIN Branches b ON s.Branch_ID = b.Branch_ID;

-- Courses Table
INSERT INTO Course_Load VALUES (Course_Seq.NEXTVAL, 'Database Systems',          4, 'Moderate');
INSERT INTO Course_Load VALUES (Course_Seq.NEXTVAL, 'Operating Systems',         4, 'Hard');
INSERT INTO Course_Load VALUES (Course_Seq.NEXTVAL, 'Computer Networks',         3, 'Moderate');
INSERT INTO Course_Load VALUES (Course_Seq.NEXTVAL, 'Data Structures and Algo',    4, 'Hard');
INSERT INTO Course_Load VALUES (Course_Seq.NEXTVAL, 'Engineering Mathematics',   3, 'Easy');
INSERT INTO Course_Load VALUES (Course_Seq.NEXTVAL, 'Software Engineering',      3, 'Moderate');
INSERT INTO Course_Load VALUES (Course_Seq.NEXTVAL, 'Digital Signal Processing', 4, 'Hard');
SELECT * from Course_Load;


-- Enrollements insertion
-- Arjun (1001): 3 courses — heavy load
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1001, 201, 2);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1001, 202, 2);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1001, 204, 2);
-- Priya (1002): 2 courses — moderate
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1002, 201, 2);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1002, 206, 2);
-- Rahul (1003): 2 courses
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1003, 203, 2);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1003, 207, 2);
-- Sneha (1004): 3 hard courses — should show very high burnout
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1004, 201, 2);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1004, 202, 2);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1004, 204, 2);
-- Vikram (1005): 1 course — light load
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1005, 205, 2);
-- Ananya (1006): 2 courses
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1006, 203, 2);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1006, 206, 2);
-- Kiran (1007): senior, 3 courses
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1007, 202, 3);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1007, 204, 3);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1007, 206, 3);
-- Divya (1008): 2 courses
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1008, 203, 3);
INSERT INTO Enrollments VALUES (Enroll_Seq.NEXTVAL, 1008, 207, 3);

select * from Enrollments;


-- Assessment Schedule table insertion
-- Mid-Sems (coming up in ~2 weeks from a typical run date)
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 201, 'Mid-Sem',    TO_DATE('15-04-2025','DD-MM-YYYY'), 30);
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 202, 'Mid-Sem',    TO_DATE('16-04-2025','DD-MM-YYYY'), 30);
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 204, 'Mid-Sem',    TO_DATE('17-04-2025','DD-MM-YYYY'), 30);
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 203, 'Mid-Sem',    TO_DATE('18-04-2025','DD-MM-YYYY'), 30);
-- Quizzes (soon)
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 201, 'Quiz',       TO_DATE('07-04-2025','DD-MM-YYYY'), 10);
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 202, 'Quiz',       TO_DATE('08-04-2025','DD-MM-YYYY'), 10);
-- Assignments
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 206, 'Assignment', TO_DATE('10-04-2025','DD-MM-YYYY'), 20);
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 204, 'Assignment', TO_DATE('09-04-2025','DD-MM-YYYY'), 15);
-- End-Sems (far out)
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 201, 'End-Sem',    TO_DATE('15-05-2025','DD-MM-YYYY'), 60);
INSERT INTO Assessments_Schedule VALUES (Assess_Seq.NEXTVAL, 202, 'End-Sem',    TO_DATE('16-05-2025','DD-MM-YYYY'), 60);
select * from Assessments_Schedule;


-- Sleep Logs Table
-- Arjun (1001): severely sleep deprived
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1001, TRUNC(SYSDATE)-6, 4.5, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1001, TRUNC(SYSDATE)-5, 5.0, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1001, TRUNC(SYSDATE)-4, 4.0, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1001, TRUNC(SYSDATE)-3, 5.5, 'Fair');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1001, TRUNC(SYSDATE)-2, 4.0, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1001, TRUNC(SYSDATE)-1, 5.0, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1001, TRUNC(SYSDATE),   4.5, 'Poor');
-- Priya (1002): healthy
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1002, TRUNC(SYSDATE)-6, 7.5, 'Good');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1002, TRUNC(SYSDATE)-5, 8.0, 'Excellent');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1002, TRUNC(SYSDATE)-4, 7.0, 'Good');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1002, TRUNC(SYSDATE)-3, 7.5, 'Good');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1002, TRUNC(SYSDATE)-2, 8.0, 'Good');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1002, TRUNC(SYSDATE)-1, 7.0, 'Good');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1002, TRUNC(SYSDATE),   7.5, 'Good');
-- Sneha (1004): critical
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1004, TRUNC(SYSDATE)-6, 3.5, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1004, TRUNC(SYSDATE)-5, 4.0, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1004, TRUNC(SYSDATE)-4, 3.0, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1004, TRUNC(SYSDATE)-3, 3.5, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1004, TRUNC(SYSDATE)-2, 4.0, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1004, TRUNC(SYSDATE)-1, 3.5, 'Poor');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1004, TRUNC(SYSDATE),   4.0, 'Poor');
-- Vikram (1005): relaxed
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1005, TRUNC(SYSDATE)-4, 8.5, 'Excellent');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1005, TRUNC(SYSDATE)-2, 8.0, 'Good');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1005, TRUNC(SYSDATE),   8.5, 'Excellent');
-- Rahul (1003): average
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1003, TRUNC(SYSDATE)-5, 6.0, 'Fair');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1003, TRUNC(SYSDATE)-3, 6.5, 'Fair');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1003, TRUNC(SYSDATE)-1, 6.0, 'Fair');
-- Ananya (1006)
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1006, TRUNC(SYSDATE)-5, 7.0, 'Good');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1006, TRUNC(SYSDATE)-2, 6.5, 'Fair');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1006, TRUNC(SYSDATE),   7.0, 'Good');
-- Kiran (1007): slightly stressed
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1007, TRUNC(SYSDATE)-4, 5.5, 'Fair');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1007, TRUNC(SYSDATE)-2, 6.0, 'Fair');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1007, TRUNC(SYSDATE),   5.5, 'Fair');
-- Divya (1008): healthy
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1008, TRUNC(SYSDATE)-4, 7.5, 'Good');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1008, TRUNC(SYSDATE)-2, 7.0, 'Good');
INSERT INTO Sleep_Logs VALUES (SleepLog_Seq.NEXTVAL, 1008, TRUNC(SYSDATE),   7.5, 'Good');

select * from sleep_logs;


-- Study_logs table
-- Arjun (1001): very high load
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1001, 201, NULL, TRUNC(SYSDATE)-6, 6.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1001, 202, NULL, TRUNC(SYSDATE)-5, 7.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1001, 204, NULL, TRUNC(SYSDATE)-4, 8.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1001, 201, NULL, TRUNC(SYSDATE)-3, 6.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1001, 202, NULL, TRUNC(SYSDATE)-2, 7.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1001, 204, NULL, TRUNC(SYSDATE)-1, 8.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1001, 201, NULL, TRUNC(SYSDATE),   7.0);
-- Priya (1002): balanced
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1002, 201, NULL, TRUNC(SYSDATE)-6, 3.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1002, 206, NULL, TRUNC(SYSDATE)-5, 2.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1002, 201, NULL, TRUNC(SYSDATE)-3, 3.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1002, 206, NULL, TRUNC(SYSDATE)-1, 2.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1002, 201, NULL, TRUNC(SYSDATE),   3.0);
-- Sneha (1004): extreme
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1004, 201, NULL, TRUNC(SYSDATE)-6, 9.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1004, 202, NULL, TRUNC(SYSDATE)-5, 8.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1004, 204, NULL, TRUNC(SYSDATE)-4, 9.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1004, 201, NULL, TRUNC(SYSDATE)-3, 8.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1004, 202, NULL, TRUNC(SYSDATE)-2, 9.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1004, 204, NULL, TRUNC(SYSDATE)-1, 8.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1004, 201, NULL, TRUNC(SYSDATE),   9.0);
-- Vikram (1005): minimal
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1005, 205, NULL, TRUNC(SYSDATE)-4, 1.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1005, 205, NULL, TRUNC(SYSDATE)-1, 2.0);
-- Rahul (1003)
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1003, 203, NULL, TRUNC(SYSDATE)-5, 4.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1003, 207, NULL, TRUNC(SYSDATE)-3, 5.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1003, 203, NULL, TRUNC(SYSDATE)-1, 4.5);
-- Ananya (1006)
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1006, 203, NULL, TRUNC(SYSDATE)-4, 3.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1006, 206, NULL, TRUNC(SYSDATE)-2, 2.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1006, 203, NULL, TRUNC(SYSDATE),   3.0);
-- Kiran (1007)
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1007, 202, NULL, TRUNC(SYSDATE)-5, 6.0);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1007, 204, NULL, TRUNC(SYSDATE)-3, 5.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1007, 206, NULL, TRUNC(SYSDATE)-1, 6.0);
-- Divya (1008)
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1008, 203, NULL, TRUNC(SYSDATE)-4, 3.5);
INSERT INTO Study_Logs VALUES (StudyLog_Seq.NEXTVAL, 1008, 207, NULL, TRUNC(SYSDATE)-2, 4.0);

select * from study_logs;

-- mood_tracker table
-- Arjun (1001): deteriorating
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1001, NULL, TRUNC(SYSDATE)-6, 5, 7);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1001, NULL, TRUNC(SYSDATE)-5, 4, 8);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1001, NULL, TRUNC(SYSDATE)-4, 4, 8);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1001, NULL, TRUNC(SYSDATE)-3, 3, 9);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1001, NULL, TRUNC(SYSDATE)-2, 3, 9);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1001, NULL, TRUNC(SYSDATE)-1, 2, 10);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1001, NULL, TRUNC(SYSDATE),   2, 10);
-- Priya (1002): positive
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1002, NULL, TRUNC(SYSDATE)-6, 8, 3);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1002, NULL, TRUNC(SYSDATE)-5, 7, 3);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1002, NULL, TRUNC(SYSDATE)-3, 8, 2);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1002, NULL, TRUNC(SYSDATE)-2, 9, 2);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1002, NULL, TRUNC(SYSDATE)-1, 7, 3);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1002, NULL, TRUNC(SYSDATE),   8, 3);
-- Sneha (1004): critical collapse
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1004, NULL, TRUNC(SYSDATE)-6, 3,  9);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1004, NULL, TRUNC(SYSDATE)-5, 2, 10);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1004, NULL, TRUNC(SYSDATE)-4, 2, 10);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1004, NULL, TRUNC(SYSDATE)-3, 1, 10);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1004, NULL, TRUNC(SYSDATE)-2, 2, 10);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1004, NULL, TRUNC(SYSDATE)-1, 1, 10);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1004, NULL, TRUNC(SYSDATE),   2, 10);
-- Vikram (1005): relaxed
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1005, NULL, TRUNC(SYSDATE)-4, 9, 1);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1005, NULL, TRUNC(SYSDATE)-1, 8, 2);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1005, NULL, TRUNC(SYSDATE),   9, 1);
-- Rahul (1003)
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1003, NULL, TRUNC(SYSDATE)-5, 6, 5);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1003, NULL, TRUNC(SYSDATE)-3, 5, 6);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1003, NULL, TRUNC(SYSDATE)-1, 6, 5);
-- Ananya (1006)
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1006, NULL, TRUNC(SYSDATE)-4, 7, 4);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1006, NULL, TRUNC(SYSDATE)-2, 6, 5);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1006, NULL, TRUNC(SYSDATE),   7, 4);
-- Kiran (1007)
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1007, NULL, TRUNC(SYSDATE)-4, 5, 7);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1007, NULL, TRUNC(SYSDATE)-2, 5, 7);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1007, NULL, TRUNC(SYSDATE),   4, 8);
-- Divya (1008)
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1008, NULL, TRUNC(SYSDATE)-3, 7, 3);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1008, NULL, TRUNC(SYSDATE)-1, 8, 2);
INSERT INTO Mood_Tracker VALUES (Mood_Seq.NEXTVAL, 1008, NULL, TRUNC(SYSDATE),   7, 3);

select * from mood_tracker;

-- extracaricular_logs table insertion
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1001, 'Football Practice', 'Sports',       TRUNC(SYSDATE)-5, 2.0);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1001, 'Coding Club',       'Club',         TRUNC(SYSDATE)-3, 1.5);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1002, 'Dance Practice',    'Cultural',     TRUNC(SYSDATE)-5, 1.5);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1002, 'NSS Volunteering',  'Volunteering', TRUNC(SYSDATE)-2, 2.0);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1003, 'Basketball',        'Sports',       TRUNC(SYSDATE)-4, 2.5);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1004, 'Drama Rehearsal',   'Cultural',     TRUNC(SYSDATE)-5, 3.0);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1004, 'Drama Rehearsal',   'Cultural',     TRUNC(SYSDATE)-3, 3.0);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1004, 'Fest Committee',    'Club',         TRUNC(SYSDATE)-1, 2.5);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1005, 'Cricket',           'Sports',       TRUNC(SYSDATE)-4, 3.0);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1006, 'Music Club',        'Club',         TRUNC(SYSDATE)-2, 1.5);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1007, 'IEEE Workshop',     'Club',         TRUNC(SYSDATE)-4, 2.0);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1007, 'IEEE Workshop',     'Club',         TRUNC(SYSDATE)-2, 2.0);
INSERT INTO Extracurricular_Logs VALUES (Extra_Seq.NEXTVAL, 1008, 'Yoga Club',         'Other',        TRUNC(SYSDATE)-2, 1.0);

select * from Extracurricular_Logs;


COMMIT ;

-- delelte values (use it just in case)
DELETE FROM Mood_Tracker;
DELETE FROM Study_Logs;
DELETE FROM Sleep_Logs;
DELETE FROM Extracurricular_Logs;
DELETE FROM Alerts;
DELETE FROM Burnout_Index;
COMMIT;

-- BURNOUT_SCORE FUNCTION
CREATE OR REPLACE FUNCTION Calculate_Burnout_Score(p_student_id IN NUMBER)
RETURN NUMBER AS
    v_avg_study   NUMBER := 0;
    v_avg_sleep   NUMBER := 8;
    v_avg_mood    NUMBER := 7;
    v_avg_stress  NUMBER := 3;
    v_avg_extra   NUMBER := 0;
    v_num_courses NUMBER := 0;
    v_score       NUMBER := 0;
BEGIN
    SELECT NVL(AVG(Study_Hours), 0) INTO v_avg_study
    FROM Study_Logs
    WHERE Student_ID = p_student_id AND Log_Date >= SYSDATE - 7;

    SELECT NVL(AVG(Sleep_Hours), 8) INTO v_avg_sleep
    FROM Sleep_Logs
    WHERE Student_ID = p_student_id AND Sleep_Date >= SYSDATE - 7;

    SELECT NVL(AVG(Mood_Rating), 7) INTO v_avg_mood
    FROM Mood_Tracker
    WHERE Student_ID = p_student_id AND Mood_Date >= SYSDATE - 7;

    SELECT NVL(AVG(Stress_Level), 3) INTO v_avg_stress
    FROM Mood_Tracker
    WHERE Student_ID = p_student_id AND Mood_Date >= SYSDATE - 7;

    SELECT NVL(AVG(Hours_Spent), 0) INTO v_avg_extra
    FROM Extracurricular_Logs
    WHERE Student_ID = p_student_id AND Activity_Date >= SYSDATE - 7;

    SELECT COUNT(*) INTO v_num_courses
    FROM Enrollments WHERE Student_ID = p_student_id;

    -- Formula: weighted sum of 5 signals, clamped 0–100
    v_score :=
        (GREATEST(v_avg_study  - 6, 0) * 8)     -- study overload
      + (GREATEST(7 - v_avg_sleep, 0) * 8)       -- sleep deficit
      + ((10 - v_avg_mood)  * 3)                 -- low mood
      + (v_avg_stress       * 2)                 -- high stress
      + (GREATEST(v_avg_extra - 2, 0) * 3)       -- extra load
      + (GREATEST(v_num_courses - 2, 0) * 2);    -- course overload

    RETURN LEAST(GREATEST(ROUND(v_score, 2), 0), 100);
EXCEPTION
    WHEN OTHERS THEN RETURN 0;
END;
/
-- burnout index function test
SELECT Student_ID,Name ,Calculate_Burnout_Score(Student_ID) AS Score
FROM Students
ORDER BY Score DESC;



-- Burnout Profiling procedure
CREATE OR REPLACE PROCEDURE Refresh_Burnout_Index(p_student_id IN NUMBER) AS
    v_score      NUMBER;
    v_level      VARCHAR2(10);
    v_confidence NUMBER;
    v_existing   NUMBER;
BEGIN
    v_score := Calculate_Burnout_Score(p_student_id);

    IF    v_score < 25 THEN v_level := 'Low';
    ELSIF v_score < 50 THEN v_level := 'Moderate';
    ELSIF v_score < 75 THEN v_level := 'High';
    ELSE                    v_level := 'Critical';
    END IF;

    -- Confidence = number of days with study data in last 7 days
    SELECT COUNT(DISTINCT TRUNC(Log_Date)) INTO v_confidence
    FROM Study_Logs
    WHERE Student_ID = p_student_id AND Log_Date >= SYSDATE - 7;

    SELECT COUNT(*) INTO v_existing
    FROM Burnout_Index WHERE Student_ID = p_student_id;

    IF v_existing > 0 THEN
        UPDATE Burnout_Index
        SET Calculated_Risk_Score = v_score,
            Risk_Level            = v_level,
            Confidence_Score      = v_confidence,
            Calculated_At         = SYSTIMESTAMP
        WHERE Student_ID = p_student_id;
    ELSE
        INSERT INTO Burnout_Index VALUES
            (Burnout_Seq.NEXTVAL, p_student_id,
             v_score, v_level, v_confidence, SYSTIMESTAMP);
    END IF;

    -- Auto-alert if High or Critical
    IF v_level IN ('High', 'Critical') THEN
        INSERT INTO Alerts VALUES (
            Alert_Seq.NEXTVAL,
            p_student_id,
            'Burnout Risk: ' || v_level,
            v_score,
            CASE v_level
                WHEN 'Critical' THEN
                    'Immediate counsellor referral recommended. Reduce course load.'
                ELSE
                    'Suggest reducing study hours and improving sleep schedule.'
            END,
            SYSTIMESTAMP
        );
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error refreshing student ' || p_student_id || ': ' || SQLERRM);
END;
/



-- Trigger 1: New sleep entry → recalculate burnout
CREATE OR REPLACE TRIGGER trg_sleep_burnout
AFTER INSERT ON Sleep_Logs
FOR EACH ROW
BEGIN
    Refresh_Burnout_Index(:NEW.Student_ID);
END;
/

-- Trigger 2: New study entry → recalculate burnout
CREATE OR REPLACE TRIGGER trg_study_burnout
AFTER INSERT ON Study_Logs
FOR EACH ROW
BEGIN
    Refresh_Burnout_Index(:NEW.Student_ID);
END;
/

-- Trigger 3: New mood entry → recalculate burnout
CREATE OR REPLACE TRIGGER trg_mood_burnout
AFTER INSERT ON Mood_Tracker
FOR EACH ROW
BEGIN
    Refresh_Burnout_Index(:NEW.Student_ID);
END;
/
-- triggers test
SELECT trigger_name, status
FROM user_triggers
WHERE trigger_name IN ('TRG_SLEEP_BURNOUT','TRG_STUDY_BURNOUT','TRG_MOOD_BURNOUT');



CREATE OR REPLACE PACKAGE Wellness_Pkg AS
    FUNCTION  Get_Risk_Level(p_student_id NUMBER) RETURN VARCHAR2;
    PROCEDURE Print_Wellness_Report(p_student_id IN NUMBER);
    PROCEDURE Refresh_All_Students;
END Wellness_Pkg;
/

CREATE OR REPLACE PACKAGE BODY Wellness_Pkg AS

    FUNCTION Get_Risk_Level(p_student_id NUMBER) RETURN VARCHAR2 AS
        v_level VARCHAR2(10);
    BEGIN
        SELECT NVL(Risk_Level, 'Unknown') INTO v_level
        FROM Burnout_Index WHERE Student_ID = p_student_id;
        RETURN v_level;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN RETURN 'Not Calculated';
    END;

    PROCEDURE Print_Wellness_Report(p_student_id IN NUMBER) AS
        v_name   Students.Name%TYPE;
        v_score  NUMBER;
        v_level  VARCHAR2(10);
        v_sleep  NUMBER;
        v_study  NUMBER;
        v_mood   NUMBER;
        v_stress NUMBER;
    BEGIN
        SELECT Name INTO v_name FROM Students WHERE Student_ID = p_student_id;

        SELECT NVL(Calculated_Risk_Score,0), NVL(Risk_Level,'N/A')
        INTO v_score, v_level
        FROM Burnout_Index WHERE Student_ID = p_student_id;

        SELECT NVL(ROUND(AVG(Sleep_Hours),1), 0) INTO v_sleep
        FROM Sleep_Logs
        WHERE Student_ID = p_student_id AND Sleep_Date >= SYSDATE - 7;

        SELECT NVL(ROUND(AVG(Study_Hours),1), 0) INTO v_study
        FROM Study_Logs
        WHERE Student_ID = p_student_id AND Log_Date >= SYSDATE - 7;

        SELECT NVL(ROUND(AVG(Mood_Rating),1), 0),
               NVL(ROUND(AVG(Stress_Level),1), 0)
        INTO v_mood, v_stress
        FROM Mood_Tracker
        WHERE Student_ID = p_student_id AND Mood_Date >= SYSDATE - 7;

        DBMS_OUTPUT.PUT_LINE('==============================');
        DBMS_OUTPUT.PUT_LINE('Student : ' || v_name || ' (ID: ' || p_student_id || ')');
        DBMS_OUTPUT.PUT_LINE('Score   : ' || v_score || ' / 100');
        DBMS_OUTPUT.PUT_LINE('Risk    : ' || v_level);
        DBMS_OUTPUT.PUT_LINE('Sleep   : ' || v_sleep || ' hrs/day (7d avg)');
        DBMS_OUTPUT.PUT_LINE('Study   : ' || v_study || ' hrs/day (7d avg)');
        DBMS_OUTPUT.PUT_LINE('Mood    : ' || v_mood  || ' / 10');
        DBMS_OUTPUT.PUT_LINE('Stress  : ' || v_stress || ' / 10');
        DBMS_OUTPUT.PUT_LINE('==============================');
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            DBMS_OUTPUT.PUT_LINE('No burnout data found for student ' || p_student_id);
    END;

    PROCEDURE Refresh_All_Students AS
        CURSOR c_all IS SELECT Student_ID FROM Students;
    BEGIN
        FOR s IN c_all LOOP
            Refresh_Burnout_Index(s.Student_ID);
            DBMS_OUTPUT.PUT_LINE(
                'Student ' || s.Student_ID ||
                ' → ' || Get_Risk_Level(s.Student_ID)
            );
        END LOOP;
    END;

END Wellness_Pkg;
/

SET SERVEROUTPUT ON;
EXEC Wellness_Pkg.Refresh_All_Students;




-- verification querries :
-- 1. Enrollment counts per student
SELECT s.Name, COUNT(e.Course_ID) AS Courses
FROM Students s JOIN Enrollments e ON s.Student_ID = e.Student_ID
GROUP BY s.Name ORDER BY Courses DESC;

-- 2. Average sleep this week per student
SELECT s.Name, ROUND(AVG(sl.Sleep_Hours),1) AS Avg_Sleep
FROM Sleep_Logs sl JOIN Students s ON sl.Student_ID = s.Student_ID
WHERE sl.Sleep_Date >= SYSDATE - 7
GROUP BY s.Name ORDER BY Avg_Sleep ASC;

-- 3. All alerts generated
SELECT s.Name, a.Alert_Type, a.Triggered_Score,
       TO_CHAR(a.Created_At,'DD-Mon HH24:MI') AS Time
FROM Alerts a JOIN Students s ON a.Student_ID = s.Student_ID
ORDER BY a.Created_At DESC;

-- 4. Stress level in 7 days before each assessment (the correlation query)
SELECT c.Course_Name, a.Assessment_Type,
       ROUND(AVG(mt.Stress_Level),1) AS Pre_Exam_Stress
FROM Assessments_Schedule a
JOIN Course_Load c   ON a.Course_ID   = c.Course_ID
JOIN Enrollments e   ON e.Course_ID   = a.Course_ID
JOIN Mood_Tracker mt ON mt.Student_ID = e.Student_ID
                     AND mt.Mood_Date BETWEEN a.Assessment_Date - 7
                                         AND a.Assessment_Date
GROUP BY c.Course_Name, a.Assessment_Type
ORDER BY Pre_Exam_Stress DESC;

COMMIT ;
