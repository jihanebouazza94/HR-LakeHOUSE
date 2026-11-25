#!/usr/bin/env python3

import json
import random
import time
import uuid
from datetime import datetime

from kafka import KafkaProducer


# Kafka configuration
KAFKA_SERVER = "localhost:9092"
TOPIC = "invoices"


# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value:
        json.dumps(value).encode("utf-8")
)


categories = [ "Electronics", "Clothing", "Food", "Books", "Furniture" ]


def generate_invoice():



    invoice = { 
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "category": random.choice(categories), 
    "price": round(random.uniform(10, 1000), 2) 
    }


    return invoice




while True:

    invoice = generate_invoice()

    # Send invoice to Kafka
    future = producer.send(
        TOPIC,
        value=invoice
    )

    # Wait until Kafka acknowledges the message
    metadata = future.get(timeout=10)

    print(
        f"Invoice sent: "
        f"{invoice['category']} | "
    )

    # Generate an invoice every 2 seconds
    time.sleep(2)
