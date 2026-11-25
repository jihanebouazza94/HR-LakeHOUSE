"""Append raw Kafka events to Bronze Parquet with checkpoints."""
import os
from pyspark.sql import SparkSession,functions as F
spark=SparkSession.builder.appName('HR-Bronze').getOrCreate()
base=os.getenv('HDFS_URI','hdfs://namenode:8020')
stream=(spark.readStream.format('kafka').option('kafka.bootstrap.servers',os.getenv('KAFKA_BOOTSTRAP','broker:29092')).option('subscribe',','.join('hr.'+t for t in ['employees','departments','jobs','salaries','attendance','leave_requests'])).option('startingOffsets','earliest').load())
bronze=stream.select('topic','partition','offset','timestamp',F.col('value').cast('string').alias('raw_json')).withColumn('ingested_at',F.current_timestamp())
query=(bronze.writeStream.format('parquet').outputMode('append').option('path',base+'/data/bronze/hr/events').option('checkpointLocation','/checkpoints/hr-bronze').trigger(processingTime='20 seconds').start())
query.awaitTermination()
