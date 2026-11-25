"""Batch Bronze -> Silver -> Gold; educational snapshot rebuild, not a production CDC merge."""
import os
from pyspark.sql import SparkSession,functions as F,Window
from pyspark.sql.types import StructType,StructField,StringType
spark=SparkSession.builder.appName('HR-Silver-Gold').getOrCreate()
base=os.getenv('HDFS_URI','hdfs://namenode:8020')+'/data'
raw=spark.read.parquet(base+'/bronze/hr/events')
events=(raw.select('*',F.get_json_object('raw_json','$.source_table').alias('entity'),F.get_json_object('raw_json','$.key').alias('business_key'),F.get_json_object('raw_json','$.after').alias('payload'),F.get_json_object('raw_json','$.op').alias('operation')))
valid=events.filter(F.col('entity').isNotNull() & F.col('business_key').isNotNull() & F.col('payload').isNotNull())
events.subtract(valid).write.mode('overwrite').parquet(base+'/quarantine/hr/invalid_events')
window=Window.partitionBy('entity','business_key').orderBy(F.col('timestamp').desc(),F.col('partition').desc(),F.col('offset').desc())
latest=valid.withColumn('rn',F.row_number().over(window)).filter('rn=1').filter("operation <> 'delete'")
tables=['employees','departments','jobs','salaries','attendance','leave_requests']
for table in tables:
 rows=latest.filter(F.col('entity')==table).select('payload')
 if rows.rdd.isEmpty():continue
 # schema inferred from JSON payload for this local demonstration
 df=spark.read.json(rows.rdd.map(lambda r:r.payload))
 df.dropDuplicates([{'employees':'employee_id','departments':'department_id','jobs':'job_id','salaries':'salary_id','attendance':'attendance_id','leave_requests':'leave_id'}[table]]).write.mode('overwrite').parquet(base+'/silver/hr/'+table)
 print('Silver written:',table)
emp=spark.read.parquet(base+'/silver/hr/employees')
dep=spark.read.parquet(base+'/silver/hr/departments')
sal=spark.read.parquet(base+'/silver/hr/salaries')
att=spark.read.parquet(base+'/silver/hr/attendance')
leave=spark.read.parquet(base+'/silver/hr/leave_requests')
head=(emp.filter(F.col('employment_status')=='Active').groupBy('department_id').agg(F.count('*').alias('headcount')).join(dep,'department_id','left'))
head.write.mode('overwrite').parquet(base+'/gold/hr/headcount_by_department')
latest_sal=sal.withColumn('rn',F.row_number().over(Window.partitionBy('employee_id').orderBy(F.col('effective_date').desc(),F.col('salary_id').desc()))).filter('rn=1')
latest_sal.join(emp.select('employee_id','department_id'),'employee_id').groupBy('department_id').agg(F.avg(F.col('base_salary').cast('double')).alias('avg_salary')).join(dep,'department_id','left').write.mode('overwrite').parquet(base+'/gold/hr/salary_by_department')
att.groupBy('status').agg(F.count('*').alias('records')).write.mode('overwrite').parquet(base+'/gold/hr/attendance_by_status')
leave.groupBy('leave_type','approval_status').agg(F.count('*').alias('requests')).write.mode('overwrite').parquet(base+'/gold/hr/leave_summary')
emp.groupBy(F.date_format(F.to_date('hire_date'),'yyyy-MM').alias('month')).agg(F.count('*').alias('hires')).write.mode('overwrite').parquet(base+'/gold/hr/hiring_trends')
print('Gold datasets created. These are snapshot calculations; no production guarantees.')
