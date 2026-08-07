import sqlite3
import json

json_file = r"D:\Agent\data\company_tickers.json"
db_file = r"D:\Agent\Database\ATS.db"

table_name = "SEC_companies"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# READ JSON
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# SEC JSON is a dict of dicts -> convert to list
rows = list(data.values())

# DROP TABLE IF EXISTS
cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# CREATE TABLE
cursor.execute(f"""
CREATE TABLE {table_name} (
    cik_str INTEGER,
    ticker TEXT,
    title TEXT
)
""")

# INSERT
cursor.executemany(
    f"""
    INSERT INTO {table_name}
    (cik_str, ticker, title)
    VALUES (?, ?, ?)
    """,
    [
        (
            row.get("cik_str"),
            row.get("ticker"),
            row.get("title")
        )
        for row in rows
    ]
)

conn.commit()

# CHECK
cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
count = cursor.fetchone()[0]

conn.close()

print(f"Created table {table_name} with {count:,} rows")