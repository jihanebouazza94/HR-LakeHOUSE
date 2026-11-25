from kafka import KafkaProducer, KafkaConsumer

BOOTSTRAP_SERVER = "localhost:9092"
TOPIC = "my-topic"

# -----------------------------
# Producer
# -----------------------------

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVER
)

print("Sending message...")

future = producer.send(
    TOPIC,
    value=b"Hello, Kafka!"
)

producer.flush()

metadata = future.get(timeout=10)

print(
    f"Message sent successfully: "
    f"topic={metadata.topic}, "
    f"partition={metadata.partition}, "
    f"offset={metadata.offset}"
)

producer.close()


# -----------------------------
# Consumer
# -----------------------------

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,

    # IMPORTANT
    auto_offset_reset="earliest",

    # Use a new group for testing
    group_id="my-test-group",

    enable_auto_commit=True,

    consumer_timeout_ms=10000
)

print("Waiting for messages...")

for message in consumer:

    print(
        f"Received: {message.value.decode('utf-8')} "
        f"(partition={message.partition}, "
        f"offset={message.offset})"
    )

consumer.close()