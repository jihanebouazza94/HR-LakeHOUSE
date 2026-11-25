from pyhive import hive

conn = hive.Connection(
    host="localhost",
    port=10000,
    username="hive",
    database="hr_gold",
    auth="NONE"
)

cursor = conn.cursor()

tables = [
    "headcount_by_department",
    "salary_by_department",
    "attendance_by_status",
    "leave_summary",
    "hiring_trends"
]

for table in tables:

    print("\n" + "=" * 60)
    print("TABLE:", table)
    print("=" * 60)

    cursor.execute(f"DESCRIBE {table}")

    print("\nSCHEMA:")
    for row in cursor.fetchall():
        print(row)

    cursor.execute(f"SELECT * FROM {table} LIMIT 20")

    print("\nCOLUMNS:")
    print([col[0] for col in cursor.description])

    print("\nDATA:")
    for row in cursor.fetchall():
        print(row)

cursor.close()
conn.close()

print("\nAll Gold tables successfully queried!")