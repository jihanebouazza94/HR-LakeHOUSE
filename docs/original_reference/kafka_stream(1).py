from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json,
    col,
    sum,
    count,
    avg
)
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType
)

# --------------------------------------------------
# Spark
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("KafkaStreaming")
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7"
    )
    .config("spark.hadoop.fs.defaultFS", "file:///")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# --------------------------------------------------
# Invoice schema
# --------------------------------------------------

schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("category", StringType(), True),
    StructField("price", DoubleType(), True)
])


# --------------------------------------------------
# Read invoices from Kafka
# --------------------------------------------------

kafka_df = (
    spark.readStream
    .format("kafka")
    .option(
        "kafka.bootstrap.servers",
        "localhost:9092"
    )
    .option(
        "subscribe",
        "invoices"
    )
    .option(
        "startingOffsets",
        "earliest"
    )
    .load()
)


# --------------------------------------------------
# Kafka value -> JSON -> columns
# --------------------------------------------------

invoices = (
    kafka_df
    .selectExpr(
        "CAST(value AS STRING) AS json"
    )
    .select(
        from_json(
            col("json"),
            schema
        ).alias("data")
    )
    .select("data.*")
)


# --------------------------------------------------
# Aggregate by category
# --------------------------------------------------

result = (
    invoices
    .groupBy("category")
    .agg(
        sum("price").alias("total_amount"),
        count("*").alias("invoice_count"),
        avg("price").alias("average_price")
    )
)


# --------------------------------------------------
# Write aggregation to console
# --------------------------------------------------

query = (
    result
    .writeStream
    .outputMode("complete")
    .format("console")
    .option(
        "truncate",
        "false"
    )
    .option(
        "numRows",
        50
    )
    .option(
        "checkpointLocation",
        "/tmp/invoice-checkpoint"
    )
    .start()
)


# --------------------------------------------------
# Keep streaming application running
# --------------------------------------------------

query.awaitTermination()
