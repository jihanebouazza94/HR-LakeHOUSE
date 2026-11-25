# HR Analytics Data Lakehouse — prototype pédagogique

## Architecture
SQL Server (source RH) → Kafka (6 topics) → Spark Structured Streaming → HDFS Bronze → Spark batch Silver → Gold → Hive/Beeline (option expérimental) et Spark SQL.

Le projet réutilise l'idée de producteur Kafka, Spark Streaming, HDFS et reporting du TP de ventes, mais remplace les factures par six entités RH. Le producteur Python effectue un **polling comparatif**, pas du Debezium CDC : il détecte les insertions et modifications visibles, mais **pas les suppressions**. Les snapshots ne fournissent pas de garanties transactionnelles CDC. Les modifications de tables SQL Server doivent être commitées avant l'interrogation.

## Ressources
Windows 11 / Docker Desktop / WSL2, RAM physique 8 Go, WSL ~5 Go. **Attention : SQL Server 2 Go + Kafka + HDFS + Spark + Hive excèdent probablement la mémoire disponible.** Préférer une VM/cloud 16–24 Go pour l'intégration complète. Les profils réduisent les services lancés, mais le streaming SQL Server → Kafka → Spark → HDFS nécessite leur fonctionnement simultané. Ne pas prétendre que l'ensemble a été testé sur 8 Go.

## Prérequis
- Docker Desktop + WSL2, Docker Compose v2, Python 3.11, Git Bash ou WSL bash.
- Pour les scripts Python locaux SQL Server : Microsoft ODBC Driver 18 for SQL Server, `pip install pyodbc kafka-python`.
- Pour exécuter `schema.sql`, utiliser Azure Data Studio, SSMS ou `sqlcmd` (l'outil n'est pas inclus dans le conteneur serveur).
- Pour Spark, prévoir les packages Kafka correspondant à Spark 3.5.5 et Hadoop HDFS client; leur téléchargement nécessite un accès réseau.

## Mise en route (PowerShell)
```powershell
Copy-Item .env.example .env
# Editer .env et définir un mot de passe fort
# Vérifier la configuration
 docker compose --profile source --profile ingest --profile storage --profile processing config
# Démarrer la source SQL Server
 docker compose --profile source up -d
# Vérifier le démarrage
 docker compose --profile source logs -f sqlserver
```

Exécuter `sqlserver/schema.sql` contre le serveur `localhost,1433` avec SSMS/sqlcmd. Installer les dépendances Python et lancer `python sqlserver/seed.py` depuis le répertoire racine (mot de passe exporté dans l'environnement). Ensuite :

```powershell
 docker compose --profile ingest up -d
 bash kafka/create_topics.sh
 docker compose --profile storage up -d
 docker compose --profile processing build
 docker compose --profile processing up -d
```

Le producteur doit voir SQL Server et Kafka : depuis Windows PowerShell, définir `SQLSERVER_HOST=localhost`, `KAFKA_BOOTSTRAP=localhost:9092` et `MSSQL_SA_PASSWORD` dans l'environnement avant `python producers/sqlserver_to_kafka.py`.

**Démarrage Spark** (le conteneur Spark doit pouvoir joindre Kafka et HDFS; les trois profils doivent rester actifs) :
```bash
 docker compose --profile processing exec spark /opt/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5 /workspace/spark/bronze_stream.py
```

Après avoir reçu des événements et arrêté le job Bronze, lancer la reconstruction Silver/Gold :
```bash
 docker compose --profile processing exec spark /opt/spark/bin/spark-submit /workspace/spark/build_silver_gold.py
 docker compose --profile storage exec namenode hdfs dfs -ls /data/gold/hr
```

**Important :** l'image Spark peut nécessiter des JARs supplémentaires et une configuration de connectivité HDFS. Le script Gold fait des overwrites sur Parquet, ce qui est approprié pour une démonstration batch hors streaming, mais **pas pour des mises à jour atomiques en production**. Les validations métiers complètes, KPI turnover/absentéisme, et Iceberg ne sont pas encore implémentés.

## Hive — intégration expérimentale
Le profil `query` est une base de configuration, **non opérationnelle sans ajustements** : driver JDBC PostgreSQL, initialisation du schéma metastore, configuration Hive et compatibilité Parquet doivent être vérifiés. Ne pas lancer le profil `query` en supposant qu'il fonctionne immédiatement. `sql/hive_gold.sql` est un exemple DDL à adapter aux types Parquet réellement écrits.

## Tests
`python -m pytest -q` exécute uniquement les tests structurels. Ce ne sont pas des tests end-to-end. Les résultats dépendent de l'environnement.

## Limites connues
- Docker Compose non exécuté ici ; compatibilité des images et configurations à vérifier.
- SQL Server et Spark simultanés probablement trop lourds pour 5 Go WSL.
- Le polling de tables sans CDC transactionnel peut manquer les suppressions et les changements transitoires.
- Recréation Silver/Gold batch : snapshots non atomiques et aucune historisation SCD2.
- L'ordre des événements de partitions Kafka différentes n'est pas un ordre global garanti.
- `latest` par timestamp Kafka est une approximation pour les updates; pas une séquence CDC stricte.
- Hive et Jupyter sont des points d'extension, pas des intégrations finalisées.
- Le pipeline ne calcule qu'un sous-ensemble des KPI RH prévus.

## Références internes
`docs/DEMO.md` : démonstration en français.
`sqlserver/schema.sql` : schéma RH.
`sqlserver/seed.py` : données synthétiques.
`producers/sqlserver_to_kafka.py` : producteur incrémental.
`spark/bronze_stream.py` et `spark/build_silver_gold.py` : traitement.
