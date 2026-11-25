"""Export HR Gold datasets from HDFS to PostgreSQL for Metabase."""

import os
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("HR-Gold-to-PostgreSQL")
    .getOrCreate()
)

HDFS_BASE = "hdfs://namenode:8020/data/gold/hr"

JDBC_URL = "jdbc:postgresql://metastore-db:5432/hr_reporting"

TABLES = [
    "headcount_by_department",
    "salary_by_department",
    "attendance_by_status",
    "leave_summary",
    "hiring_trends",
]

password = os.environ["POSTGRES_PASSWORD"]

for table in TABLES:
    print(f"\nExporting {table}...", flush=True)

    df = spark.read.parquet(f"{HDFS_BASE}/{table}")

    count = df.count()

    (
        df.coalesce(1)
        .write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", table)
        .option("user", "hive")
        .option("password", password)
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")
        .save()
    )

    print(f"Exported {table}: {count} rows", flush=True)

print("\nAll five Gold datasets exported successfully.", flush=True)

spark.stop()