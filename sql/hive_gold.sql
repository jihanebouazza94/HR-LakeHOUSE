-- Run only after HDFS and Hive services are confirmed working.
CREATE DATABASE IF NOT EXISTS hr_gold;
CREATE EXTERNAL TABLE IF NOT EXISTS hr_gold.headcount_by_department (
 department_id STRING, headcount BIGINT, department_name STRING, location STRING
) STORED AS PARQUET LOCATION 'hdfs://namenode:8020/data/gold/hr/headcount_by_department';
SELECT * FROM hr_gold.headcount_by_department LIMIT 20;
-- Spark's inferred Parquet types may require DDL adjustments; validate with parquet-tools.
