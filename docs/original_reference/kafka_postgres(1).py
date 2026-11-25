from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json,
    col,
    sum,
    count,
    avg,
    lit,
    current_timestamp
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
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7,"
    )
    .config("spark.hadoop.fs.defaultFS", "file:///")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


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
# Write each micro-batch to PostgreSQL
# --------------------------------------------------

def write_to_postgres(batch_df, batch_id):

    # Avoid writing empty batches
    if batch_df.isEmpty():
        return

    print("-------------------------------------------")
    print(f"Batch: {batch_id}")
    print("-------------------------------------------")

    # Add batch ID and processing timestamp
    output_df = (
        batch_df
        .withColumn(
            "batch_id",
            lit(batch_id)
        )
        .withColumn(
            "processed_at",
            current_timestamp()
        )
    )

    # Display the result
    output_df.show(
        truncate=False
    )

    # --------------------------------------------------
    # Write to PostgreSQL
    # --------------------------------------------------

    (
        output_df.write
        .format("jdbc")
        .option(
            "url",
            "jdbc:postgresql://localhost:5432/streaming"
        )
        .option(
            "dbtable",
            "sales"
        )
        .option(
            "user",
            "postgres"
        )
        .option(
            "password",
            "postgres"
        )
        .option(
            "driver",
            "org.postgresql.Driver"
        )
        .mode("append")
        .save()
    )

    print(
        f"Batch {batch_id} written to PostgreSQL"
    )


# --------------------------------------------------
# Start streaming
# --------------------------------------------------

query = (
    result.writeStream
    .outputMode("complete")
    .foreachBatch(write_to_postgres)
    .option(
        "checkpointLocation",
        "/tmp/checkpoints/sales"
    )
    .start()
)


# --------------------------------------------------
# Wait for streaming to finish
# --------------------------------------------------

query.awaitTermination()

