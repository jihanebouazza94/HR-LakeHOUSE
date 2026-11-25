# Demo script (French)
1. « Voici la base RH SQL Server avec 500 employés fictifs. » Vérifier `SELECT COUNT(*) FROM dbo.employees`.
2. « Kafka transporte les changements RH. » Ouvrir http://localhost:9000 et les topics hr.*.
3. « Spark consomme ces événements en streaming. » Montrer les logs du job Bronze.
4. « HDFS stocke les données brutes. » Lister `/data/bronze/hr/events`.
5. « La transformation Silver conserve la dernière version de chaque enregistrement. » Lister `/data/silver/hr`.
6. « Gold calcule les indicateurs RH. » Montrer les tables Parquet et les résultats Spark.
7. Hive est une intégration optionnelle à valider avant de la présenter comme opérationnelle.
