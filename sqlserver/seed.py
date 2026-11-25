"""Seed SQL Server using pyodbc on Windows/WSL with ODBC Driver 18 installed."""
import os,random,datetime
import pyodbc
random.seed(42)
server=os.getenv('SQLSERVER_HOST','localhost')
password=os.environ['MSSQL_SA_PASSWORD']
conn=pyodbc.connect(f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server},1433;DATABASE=HRAnalytics;UID=sa;PWD={password};Encrypt=yes;TrustServerCertificate=yes')
c=conn.cursor()
for i,name in enumerate(['Engineering','Finance','Human Resources','Operations','Sales','Support'],1):
 c.execute('IF NOT EXISTS (SELECT 1 FROM dbo.departments WHERE department_id=?) INSERT INTO dbo.departments VALUES (?,?,?)',i,i,name,'Rabat')
for i,name in enumerate(['Analyst','Engineer','Specialist','Manager','Coordinator'],1):
 c.execute('IF NOT EXISTS (SELECT 1 FROM dbo.jobs WHERE job_id=?) INSERT INTO dbo.jobs VALUES (?,?,?)',i,i,name,i)
for i in range(1,501):
 hire=datetime.date(2018,1,1)+datetime.timedelta(days=random.randint(0,2500))
 status='Terminated' if i%17==0 else 'Active'
 term=hire+datetime.timedelta(days=365) if status=='Terminated' else None
 c.execute("""IF NOT EXISTS (SELECT 1 FROM dbo.employees WHERE employee_id=?) INSERT INTO dbo.employees(employee_id,first_name,last_name,gender,birth_date,hire_date,department_id,job_id,manager_id,employment_status,termination_date) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",i,i,'Employee',f'{i:04d}',random.choice(['F','M']),datetime.date(1980,1,1)+datetime.timedelta(days=i*9),hire,1+i%6,1+i%5,None,status,term)
 c.execute('IF NOT EXISTS (SELECT 1 FROM dbo.salaries WHERE salary_id=?) INSERT INTO dbo.salaries(salary_id,employee_id,base_salary,bonus,effective_date) VALUES (?,?,?,?,?)',i,i,i,4000+i*13,round(i%9*100.0,2),hire)
 for d in range(1,8):
  k=i*10+d; day=datetime.date(2026,10,d)
  c.execute('IF NOT EXISTS (SELECT 1 FROM dbo.attendance WHERE attendance_id=?) INSERT INTO dbo.attendance(attendance_id,employee_id,attendance_date,status) VALUES (?,?,?,?)',k,k,i,day,'Absent' if (i+d)%11==0 else 'Present')
 if i%10==0:
  c.execute('IF NOT EXISTS (SELECT 1 FROM dbo.leave_requests WHERE leave_id=?) INSERT INTO dbo.leave_requests(leave_id,employee_id,leave_type,start_date,end_date,approval_status) VALUES (?,?,?,?,?,?)',i,i,i,'Annual',datetime.date(2026,11,1),datetime.date(2026,11,3),'Approved')
conn.commit();conn.close();print('Seeded HRAnalytics (500 employees)')
