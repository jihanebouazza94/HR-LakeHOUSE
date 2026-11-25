#!/usr/bin/env bash
set -euo pipefail
for table in employees departments jobs salaries attendance leave_requests; do
 docker compose --profile ingest exec -T broker /opt/kafka/bin/kafka-topics.sh --bootstrap-server broker:29092 --create --if-not-exists --topic "hr.$table" --partitions 3 --replication-factor 1
done
