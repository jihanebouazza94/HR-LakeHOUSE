
sudo -u postgres psql



CREATE USER postgres WITH PASSWORD 'postgres';



ALTER USER postgres WITH PASSWORD 'postgres';


GRANT ALL PRIVILEGES ON DATABASE streaming TO postgres;



\c streaming


GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;


ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO postgres;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO postgres;

Exit:

\q


psql -h localhost -U postgres -d streaming

Enter:



.option("url", "jdbc:postgresql://localhost:5432/streaming")
.option("user", "postgres")
.option("password", "postgres")
.option("driver", "org.postgresql.Driver")


sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"


psql -h localhost -U postgres -d streaming -W

Use password:

postgres



CREATE TABLE sales (
    category VARCHAR(100),
    total_amount DOUBLE PRECISION,
    invoice_count BIGINT,
    average_price DOUBLE PRECISION,
    batch_id BIGINT,
    processed_at TIMESTAMP
);