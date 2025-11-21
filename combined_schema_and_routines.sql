-- combined_schema_and_routines.sql
CREATE DATABASE IF NOT EXISTS Onlinequiz;
USE Onlinequiz;

-- DROP IN CORRECT ORDER
DROP TABLE IF EXISTS TAKE;
DROP TABLE IF EXISTS SCORE;
DROP TABLE IF EXISTS QUESTIONS;
DROP TABLE IF EXISTS QUIZ;
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS STAFF;
DROP TABLE IF EXISTS DEPARTMENT;

-- ===========================================
-- DEPARTMENT TABLE
-- ===========================================
CREATE TABLE DEPARTMENT (
  Dept_ID VARCHAR(6) NOT NULL,
  Dept_name VARCHAR(50) NOT NULL,
  PRIMARY KEY (Dept_ID),
  UNIQUE KEY unique_dept_name (Dept_name)
) ENGINE=InnoDB;

INSERT INTO DEPARTMENT VALUES
('CSE', 'Computer Science and Engineering'),
('ISE', 'Information Science and Engineering'),
('ECE', 'Electronics and Communication Engineering'),
('EEE', 'Electrical and Electronics Engineering'),
('ME', 'Mechanical Engineering');

-- ===========================================
-- STAFF TABLE
-- ===========================================
CREATE TABLE STAFF (
  Staff_ID VARCHAR(20) NOT NULL,
  st_name VARCHAR(100) NOT NULL,
  st_emailid VARCHAR(100) NOT NULL,
  Dept_ID VARCHAR(6) NOT NULL,
  st_Ph_no VARCHAR(15) NOT NULL,
  DOB DATE NOT NULL,
  st_password VARCHAR(255) NOT NULL,
  PRIMARY KEY (Staff_ID),
  UNIQUE KEY unique_staff_email (st_emailid),
  UNIQUE KEY unique_staff_phone (st_Ph_no),
  FOREIGN KEY (Dept_ID) REFERENCES DEPARTMENT(Dept_ID)
) ENGINE=InnoDB;

INSERT INTO STAFF VALUES
('STF001', 'Dr. Rajesh Kumar', 'rajesh.kumar@university.edu', 'CSE', '9876543210', '1980-05-15', '$2y$10$abcdefghijklmnopqrstuvwxyz123456'),
('STF002', 'Prof. Priya Sharma', 'priya.sharma@university.edu', 'CSE', '9876543211', '1985-08-20', '$2y$10$bcdefghijklmnopqrstuvwxyz234567'),
('STF003', 'Dr. Amit Patel', 'amit.patel@university.edu', 'ISE', '9876543212', '1982-03-10', '$2y$10$cdefghijklmnopqrstuvwxyz345678'),
('STF004', 'Prof. Sneha Reddy', 'sneha.reddy@university.edu', 'ECE', '9876543213', '1988-11-25', '$2y$10$defghijklmnopqrstuvwxyz456789'),
('STF005', 'Dr. Vikram Singh', 'vikram.singh@university.edu', 'EEE', '9876543214', '1983-07-08', '$2y$10$efghijklmnopqrstuvwxyz567890');

-- ===========================================
-- STUDENT TABLE
-- ===========================================
CREATE TABLE STUDENT (
  student_ID VARCHAR(20) NOT NULL,
  s_name VARCHAR(100) NOT NULL,
  Sem INT NOT NULL,
  s_emailid VARCHAR(100) NOT NULL,
  s_ph_no VARCHAR(15) NOT NULL,
  s_gender CHAR(1) NOT NULL,
  Date INT NOT NULL,
  Month INT NOT NULL,
  Year INT NOT NULL,
  s_password VARCHAR(255) NOT NULL,
  Dept_ID VARCHAR(6) NOT NULL,
  PRIMARY KEY (student_ID),
  UNIQUE KEY unique_student_email (s_emailid),
  UNIQUE KEY unique_student_phone (s_ph_no),
  FOREIGN KEY (Dept_ID) REFERENCES DEPARTMENT(Dept_ID)
) ENGINE=InnoDB;

INSERT INTO STUDENT VALUES
('1CS21CS001', 'Aarav Mehta', 5, 'aarav.mehta@student.edu', '8765432101', 'M', 15, 6, 2003, '$2y$10$student123456789abcdefgh', 'CSE'),
('1CS21CS002', 'Ananya Singh', 5, 'ananya.singh@student.edu', '8765432102', 'F', 22, 3, 2003, '$2y$10$student234567890bcdefghi', 'CSE'),
('1CS21CS003', 'Rohan Gupta', 5, 'rohan.gupta@student.edu', '8765432103', 'M', 10, 9, 2002, '$2y$10$student345678901cdefghij', 'CSE'),
('1IS21IS001', 'Priya Iyer', 6, 'priya.iyer@student.edu', '8765432104', 'F', 5, 12, 2002, '$2y$10$student456789012defghijk', 'ISE'),
('1EC21EC001', 'Karthik Reddy', 4, 'karthik.reddy@student.edu', '8765432105', 'M', 18, 7, 2003, '$2y$10$student567890123efghijkl', 'ECE');

CREATE TABLE STUDENT_ANSWERS (
    student_ID VARCHAR(20),
    Quiz_ID VARCHAR(10),
    Question VARCHAR(500),
    student_answer VARCHAR(200),
    PRIMARY KEY(student_ID, Quiz_ID, Question)
);

-- ===========================================
-- QUIZ TABLE
-- ===========================================
CREATE TABLE QUIZ (
  Quiz_ID VARCHAR(10) NOT NULL,
  Quiz_name VARCHAR(100) NOT NULL,
  Date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Staff_ID VARCHAR(20) NOT NULL,
  PRIMARY KEY (Quiz_ID),
  FOREIGN KEY (Staff_ID) REFERENCES STAFF(Staff_ID)
) ENGINE=InnoDB;

INSERT INTO QUIZ VALUES
('UE23252', 'Data Structures - Mid Term', '2024-09-15 10:00:00', 'STF001'),
('UE23242', 'Database Management Systems Quiz', '2024-09-20 14:30:00', 'STF002'),
('UE23243', 'Object Oriented Programming Test', '2024-09-25 09:00:00', 'STF001'),
('UE23253', 'Computer Networks Quiz 1', '2024-10-01 11:00:00', 'STF003'),
('UE23254', 'Digital Electronics Assessment', '2024-10-05 15:00:00', 'STF004');

-- ===========================================
-- QUESTIONS TABLE (WITH MARKS)
-- ===========================================

CREATE TABLE QUESTIONS (
  Question_ID INT AUTO_INCREMENT,
  Question VARCHAR(500) NOT NULL,
  Staff_ID VARCHAR(20) NOT NULL,
  Option1 VARCHAR(200) NOT NULL,
  Option2 VARCHAR(200) NOT NULL,
  Option3 VARCHAR(200) NOT NULL,
  Option4 VARCHAR(200) NOT NULL,
  Answer VARCHAR(200) NOT NULL,
  Quiz_ID VARCHAR(10) NOT NULL,
  Marks INT NOT NULL DEFAULT 1,

  PRIMARY KEY (Question_ID),

  UNIQUE KEY uq_question_unique (Quiz_ID, Question),

  FOREIGN KEY (Staff_ID) REFERENCES STAFF(Staff_ID),
  FOREIGN KEY (Quiz_ID) REFERENCES QUIZ(Quiz_ID)
) ENGINE=InnoDB;


INSERT INTO QUESTIONS VALUES
(1, 'What is the time complexity of binary search?', 'STF001','O(n)','O(log n)','O(n^2)','O(1)','O(log n)','UE23252',2),
(2, 'Which data structure uses LIFO principle?', 'STF001','Queue','Stack','Tree','Graph','Stack','UE23252',1),
(3, 'What does SQL stand for?', 'STF002','Structured Query Language','Simple Query Language','Standard Query Language','System Query Language','Structured Query Language','UE23242',2),
(4, 'Which normal form eliminates transitive dependencies?', 'STF002','1NF','2NF','3NF','BCNF','3NF','UE23242',2),
(5, 'What is polymorphism in OOP?', 'STF001','Data hiding','Multiple forms','Inheritance','Encapsulation','Multiple forms','UE23243',3);
-- ===========================================
-- TAKE TABLE
-- ===========================================
CREATE TABLE TAKE (
  student_id VARCHAR(20) NOT NULL,
  Quiz_ID VARCHAR(10) NOT NULL,
  PRIMARY KEY (student_id, Quiz_ID),
  FOREIGN KEY (student_id) REFERENCES STUDENT(student_ID),
  FOREIGN KEY (Quiz_ID) REFERENCES QUIZ(Quiz_ID)
) ENGINE=InnoDB;

INSERT INTO TAKE VALUES
('1CS21CS001','UE23252'),
('1CS21CS002','UE23252'),
('1CS21CS001','UE23242'),
('1CS21CS003','UE23243'),
('1IS21IS001','UE23253');

-- ===========================================
-- SCORE TABLE
-- ===========================================
CREATE TABLE SCORE (
  Score_ID VARCHAR(20) NOT NULL,
  student_ID VARCHAR(20) NOT NULL,
  Score INT NOT NULL DEFAULT 0,
  Staff_ID VARCHAR(20) NOT NULL,
  Remark VARCHAR(50),
  Quiz_ID VARCHAR(10) NOT NULL,
  PRIMARY KEY (Score_ID),
  UNIQUE KEY unique_stu_quiz (student_ID, Quiz_ID),
  FOREIGN KEY (student_ID) REFERENCES STUDENT(student_ID),
  FOREIGN KEY (Staff_ID) REFERENCES STAFF(Staff_ID),
  FOREIGN KEY (Quiz_ID) REFERENCES QUIZ(Quiz_ID)
) ENGINE=InnoDB;

INSERT INTO SCORE VALUES
('1CS21CS0011','1CS21CS001',85,'STF001','Excellent performance','UE23252'),
('1CS21CS0021','1CS21CS002',72,'STF001','Good attempt','UE23252'),
('1CS21CS0012','1CS21CS001',90,'STF002','Outstanding','UE23242'),
('1CS21CS0031','1CS21CS003',68,'STF001','Needs improvement','UE23243'),
('1IS21IS0013','1IS21IS001',78,'STF003','Good understanding','UE23253');

-- ===========================================
-- TRIGGERS
-- ===========================================
DELIMITER //

CREATE TRIGGER trg_add_remark
BEFORE INSERT ON SCORE
FOR EACH ROW
BEGIN
    IF NEW.Score >= 90 THEN SET NEW.Remark='Outstanding';
    ELSEIF NEW.Score >= 80 THEN SET NEW.Remark='Excellent';
    ELSEIF NEW.Score >= 70 THEN SET NEW.Remark='Good';
    ELSEIF NEW.Score >= 60 THEN SET NEW.Remark='Satisfactory';
    ELSEIF NEW.Score >= 50 THEN SET NEW.Remark='Pass';
    ELSE SET NEW.Remark='Fail';
    END IF;
END//

CREATE TRIGGER trg_add_take
AFTER INSERT ON SCORE
FOR EACH ROW
BEGIN
    INSERT IGNORE INTO TAKE(student_ID,Quiz_ID)
    VALUES(NEW.student_ID,NEW.Quiz_ID);
END//

CREATE TRIGGER trg_update_remark
BEFORE UPDATE ON SCORE
FOR EACH ROW
BEGIN
    IF NEW.Score <> OLD.Score THEN
        IF NEW.Score >= 90 THEN SET NEW.Remark='Outstanding';
        ELSEIF NEW.Score >= 80 THEN SET NEW.Remark='Excellent';
        ELSEIF NEW.Score >= 70 THEN SET NEW.Remark='Good';
        ELSEIF NEW.Score >= 60 THEN SET NEW.Remark='Satisfactory';
        ELSEIF NEW.Score >= 50 THEN SET NEW.Remark='Pass';
        ELSE SET NEW.Remark='Fail';
        END IF;
    END IF;
END//
DELIMITER ;

-- ===========================================
-- FUNCTIONS
-- ===========================================
DELIMITER //

CREATE FUNCTION get_student_average(stu VARCHAR(15))
RETURNS DECIMAL(6,2)
DETERMINISTIC
BEGIN
    DECLARE v DECIMAL(6,2);
    SELECT AVG(Score) INTO v FROM SCORE WHERE student_ID=stu;
    RETURN COALESCE(v,0);
END//

CREATE FUNCTION get_total_quizzes_taken(stu VARCHAR(15))
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE c INT;
    SELECT COUNT(*) INTO c FROM TAKE WHERE student_ID=stu;
    RETURN COALESCE(c,0);
END//

CREATE FUNCTION calculate_grade(score_val INT)
RETURNS VARCHAR(3)
DETERMINISTIC
BEGIN
    RETURN CASE
        WHEN score_val >= 90 THEN 'A+'
        WHEN score_val >= 80 THEN 'A'
        WHEN score_val >= 70 THEN 'B+'
        WHEN score_val >= 60 THEN 'B'
        WHEN score_val >= 50 THEN 'C'
        ELSE 'F'
    END;
END//

CREATE FUNCTION get_department_name(did VARCHAR(6))
RETURNS VARCHAR(100)
DETERMINISTIC
BEGIN
    DECLARE nm VARCHAR(100);
    SELECT Dept_name INTO nm FROM DEPARTMENT WHERE Dept_ID=did LIMIT 1;
    RETURN COALESCE(nm,'Unknown');
END//
DELIMITER ;

-- ===========================================
-- PROCEDURES
-- ===========================================
DELIMITER //

CREATE PROCEDURE get_leaderboard()
BEGIN
    SELECT sc.Score_ID, sc.student_ID, st.s_name, sc.Score, sc.Remark, q.Quiz_name
    FROM SCORE sc
    JOIN STUDENT st ON sc.student_ID=st.student_ID
    JOIN QUIZ q ON sc.Quiz_ID=q.Quiz_ID
    ORDER BY sc.Score DESC, st.s_name ASC;
END//

CREATE PROCEDURE get_student_scores(IN stu VARCHAR(15))
BEGIN
    SELECT sc.Quiz_ID, q.Quiz_name, sc.Score, sc.Remark, sc.Staff_ID
    FROM SCORE sc
    JOIN QUIZ q ON sc.Quiz_ID=q.Quiz_ID
    WHERE sc.student_ID=stu;
END//

CREATE PROCEDURE get_quiz_statistics(IN qid VARCHAR(15))
BEGIN
    SELECT q.Quiz_name,
           COUNT(sc.Score_ID),
           COALESCE(ROUND(AVG(sc.Score),2),0),
           COALESCE(MAX(sc.Score),0),
           COALESCE(MIN(sc.Score),0),
           COUNT(DISTINCT t.student_ID)
    FROM QUIZ q
    LEFT JOIN SCORE sc ON q.Quiz_ID=sc.Quiz_ID
    LEFT JOIN TAKE t ON q.Quiz_ID=t.Quiz_ID
    WHERE q.Quiz_ID=qid;
END//

CREATE PROCEDURE calculate_quiz_average(IN qid VARCHAR(15))
BEGIN
    SELECT q.Quiz_name,
           COALESCE(ROUND(AVG(sc.Score),2),0),
           COUNT(sc.Score_ID)
    FROM QUIZ q
    LEFT JOIN SCORE sc ON q.Quiz_ID=sc.Quiz_ID
    WHERE q.Quiz_ID=qid;
END//

CREATE PROCEDURE assign_quiz_to_student(IN stu VARCHAR(15), IN qid VARCHAR(15))
BEGIN
    INSERT IGNORE INTO TAKE(student_ID,Quiz_ID) VALUES(stu,qid);
    SELECT CONCAT('Assigned quiz ',qid,' to student ',stu) AS Message;
END//

CREATE PROCEDURE get_student_quiz_details(IN stu VARCHAR(15))
BEGIN
    SELECT q.Quiz_name, sc.Score, sc.Remark, sc.Staff_ID
    FROM TAKE t
    JOIN QUIZ q ON t.Quiz_ID=q.Quiz_ID
    LEFT JOIN SCORE sc ON sc.student_ID=t.student_ID AND sc.Quiz_ID=t.Quiz_ID
    WHERE t.student_ID=stu;
END//
DELIMITER ;
