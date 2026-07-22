# CREATES A COPY OF THE CHROME DATABASE
from pathlib import Path
import shutil
import sqlite3

from Exp_db_to_Excel import Exp_db_to_Excel
from Summarize_db import Summarize_db

chrome_dir = (
    Path.home()
    / "AppData"
    / "Local"
    / "Google"
    / "Chrome"
    / "User Data"
    / "Default"
)

dest_dir = Path(r"D:\Agent\Database")
new_db = dest_dir / "History"

# dest_dir.mkdir(exist_ok=True)

for file in ["History", "History-wal", "History-shm"]:
    src = chrome_dir / file
    if src.exists():
        shutil.copy2(src, dest_dir / file)

print("Chrome history copied")

# Load all visited URLs into a set
conn = sqlite3.connect(new_db)
cursor = conn.cursor()

# Create a new table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS visited_urls (
        url TEXT PRIMARY KEY,
        visited_at TEXT
    )
""")

end_count = Summarize_db(new_db, "urls", "")

# Chrome stores timestamps as microseconds since 1601-01-01 UTC
cursor.execute("""
    INSERT OR REPLACE INTO visited_urls (url, visited_at)
    SELECT
        url,
        datetime(last_visit_time / 1000000 - 11644473600, 'unixepoch')
    FROM urls
    --WHERE last_visit_time > 0
""")

conn.commit()
conn.close()

end_count = Summarize_db(new_db, "visited_urls", "")
Exp_db_to_Excel(new_db,"visited_urls","","")
