from pathlib import Path
import shutil
import sqlite3
import tempfile

# Chrome History database
history_db = (
    Path.home()
    / "AppData"
    / "Local"
    / "Google"
    / "Chrome"
    / "User Data"
    / "Default"
    / "History"
)

# Make a temporary copy (History is usually locked by Chrome)
# tmp_db = Path(tempfile.gettempdir()) / "Chrome_History_Copy.db"

tmp_db = Path(tempfile.gettempdir()) / "Chrome_History.db"

shutil.copy2(history_db, tmp_db)

# Load all visited URLs into a set
conn = sqlite3.connect(tmp_db)
cursor = conn.cursor()

# Create a new table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS visited_urls (
        url TEXT PRIMARY KEY,
        visited_at TEXT
    )
""")

# Chrome stores timestamps as microseconds since 1601-01-01 UTC
cursor.execute("""
    INSERT OR REPLACE INTO visited_urls (url, visited_at)
    SELECT
        url,
        datetime(last_visit_time / 1000000 - 11644473600, 'unixepoch')
    FROM urls
    WHERE last_visit_time > 0
""")

conn.close()
tmp_db.unlink()

# Example:
# if job["url"] in visited_urls:
#     print("Already visited")