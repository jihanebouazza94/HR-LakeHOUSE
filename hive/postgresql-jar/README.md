The Apache Hive image may require the PostgreSQL JDBC driver JAR in its classpath.
Download the appropriate official PostgreSQL JDBC JAR and mount it into /opt/hive/lib.
The current Compose mount /opt/hive/lib/external is NOT automatically on the classpath.
Hive initialization and service configuration require integration validation.
