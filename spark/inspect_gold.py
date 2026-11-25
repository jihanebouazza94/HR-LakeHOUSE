
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("HR-Gold-Schema-Inspection")
    .getOrCreate()
)

base = "hdfs://namenode:8020/data/gold/hr"

datasets = [
    "headcount_by_department",
    "salary_by_department",
    "attendance_by_status",
    "leave_summary",
    "hiring_trends",
]

for dataset in datasets:
    print(f"\n{'=' * 60}")
    print(f"DATASET: {dataset}")
    print(f"{'=' * 60}")

    df = spark.read.parquet(f"{base}/{dataset}")

    print("SCHEMA:")
    df.printSchema()

    print("SAMPLE DATA:")
    df.show(5, truncate=False)

spark.stop()
