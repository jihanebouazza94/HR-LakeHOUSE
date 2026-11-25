"""Incremental polling demonstration; NOT full CDC (deletes are not detected)."""
import os,json,time,datetime,pathlib
import pyodbc
from kafka import KafkaProducer
TOPICS={'employees':'employee_id','departments':'department_id','jobs':'job_id','salaries':'salary_id','attendance':'attendance_id','leave_requests':'leave_id'}
# Simple snapshot+change comparison. For demo only; state file persists keys/hashes.
state_path=pathlib.Path(os.getenv('STATE_FILE','/tmp/hr-producer-state.json'))
state=json.loads(state_path.read_text()) if state_path.exists() else {}
producer=KafkaProducer(bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP','localhost:9092'),value_serializer=lambda d:json.dumps(d,default=str).encode())
connection=pyodbc.connect(f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={os.getenv('SQLSERVER_HOST','localhost')},1433;DATABASE=HRAnalytics;UID=sa;PWD={os.environ['MSSQL_SA_PASSWORD']};Encrypt=yes;TrustServerCertificate=yes")
while True:
 for table,pk in TOPICS.items():
  cursor=connection.cursor();cursor.execute(f'SELECT * FROM dbo.{table}')
  cols=[d[0] for d in cursor.description]
  for row in cursor.fetchall():
   record=dict(zip(cols,row)); record={k:(v.isoformat() if isinstance(v,(datetime.date,datetime.datetime,datetime.time)) else str(v) if isinstance(v, __import__('decimal').Decimal) else v) for k,v in record.items()}
   key=f'{table}:{record[pk]}';fingerprint=json.dumps(record,sort_keys=True,default=str)
   if state.get(key)==fingerprint:continue
   producer.send('hr.'+table,{'op':'insert' if key not in state else 'update','source_table':table,'event_ts':datetime.datetime.now(datetime.timezone.utc).isoformat(),'key':record[pk],'after':record}).get(timeout=20)
   state[key]=fingerprint
  print('Checked',table)
 producer.flush();state_path.write_text(json.dumps(state));time.sleep(int(os.getenv('POLL_SECONDS','15')))
