IF DB_ID('HRAnalytics') IS NULL CREATE DATABASE HRAnalytics;
GO
USE HRAnalytics;
GO
IF OBJECT_ID('dbo.departments','U') IS NULL CREATE TABLE dbo.departments(department_id INT PRIMARY KEY, department_name NVARCHAR(100) NOT NULL, location NVARCHAR(100));
IF OBJECT_ID('dbo.jobs','U') IS NULL CREATE TABLE dbo.jobs(job_id INT PRIMARY KEY, job_title NVARCHAR(100) NOT NULL, salary_grade INT NOT NULL);
IF OBJECT_ID('dbo.employees','U') IS NULL CREATE TABLE dbo.employees(employee_id INT PRIMARY KEY, first_name NVARCHAR(80),last_name NVARCHAR(80),gender NVARCHAR(20),birth_date DATE,hire_date DATE,department_id INT REFERENCES dbo.departments(department_id),job_id INT REFERENCES dbo.jobs(job_id),manager_id INT NULL,employment_status NVARCHAR(30),termination_date DATE NULL,updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME());
IF OBJECT_ID('dbo.salaries','U') IS NULL CREATE TABLE dbo.salaries(salary_id INT PRIMARY KEY,employee_id INT NOT NULL REFERENCES dbo.employees(employee_id),base_salary DECIMAL(12,2),bonus DECIMAL(12,2),effective_date DATE,updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME());
IF OBJECT_ID('dbo.attendance','U') IS NULL CREATE TABLE dbo.attendance(attendance_id INT PRIMARY KEY,employee_id INT NOT NULL REFERENCES dbo.employees(employee_id),attendance_date DATE,check_in TIME NULL,check_out TIME NULL,status NVARCHAR(30),updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME());
IF OBJECT_ID('dbo.leave_requests','U') IS NULL CREATE TABLE dbo.leave_requests(leave_id INT PRIMARY KEY,employee_id INT NOT NULL REFERENCES dbo.employees(employee_id),leave_type NVARCHAR(40),start_date DATE,end_date DATE,approval_status NVARCHAR(30),updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME());
GO
