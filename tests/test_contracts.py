from pathlib import Path

def test_schema_exists():
 assert Path('sqlserver/schema.sql').exists()

def test_compose_exists():
 assert Path('docker-compose.yml').exists()

def test_spark_scripts_exist():
 assert Path('spark/bronze_stream.py').exists()
 assert Path('spark/build_silver_gold.py').exists()
