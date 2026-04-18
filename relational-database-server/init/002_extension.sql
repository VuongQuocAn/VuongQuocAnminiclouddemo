CREATE DATABASE IF NOT EXISTS studentdb;
USE studentdb;
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(10),
    fullname VARCHAR(100),
    dob DATE,
    major VARCHAR(50)
);

INSERT INTO students (student_id, fullname, dob, major) VALUES 
('SE001', 'Nguyen Van A', '2003-05-15', 'Software Engineering'),
('SE002', 'Tran Thi B', '2004-08-20', 'Information Technology'),
('SE003', 'Le Van C', '2003-12-10', 'Computer Science');
