python3 -m venv stream
source stream/bin/activate 
pip3 install kafka-python
pip3 install pyspark
# sample usage
docker logs broker

docker exec -it -w /opt/kafka/bin broker sh
./kafka-topics.sh --create --topic my-topic --bootstrap-server broker:9092
./kafka-console-producer.sh  --topic my-topic --bootstrap-server broker:9092


docker exec -it -w /opt/kafka/bin broker sh
./kafka-console-consumer.sh --topic my-topic --from-beginning --bootstrap-server  broker:9092



# second lab (spark streaming)

docker compose ps

docker exec broker \
  /opt/kafka/bin/kafka-topics.sh \
  --create \
  --topic transactions \
  --bootstrap-server broker:29092 \
  --partitions 3 \
  --replication-factor 1


python3 invoice_producer.py
$SPARK_HOME/sbin/start-all.sh
# for spark streaming to console 
/usr/local/spark/bin/spark-submit  \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7 \
/home/dba/Finance/project/kafka_stream.py





# add python postgresql connector
pip3 install psycopg2-binary


# for spark streaming to postgresql
spark-submit \
  --master spark://192.168.74.181:7077 \
  --jars /usr/local/spark/jars/postgresql-42.7.4.jar \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7 \
  kafka_postgres.py

