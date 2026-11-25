Use a Jupyter environment with PySpark 3.5.x configured to reach HDFS.
Example:
```python
from pyspark.sql import SparkSession
spark=SparkSession.builder.appName('HR-Analysis').getOrCreate()
df=spark.read.parquet('hdfs://namenode:8020/data/gold/hr/headcount_by_department')
df.show()
```
