# CREATES A COPY OF THE CHROME DATABASE
# THIS MAY BE THE BEST APPROACH
from pathlib import Path
import shutil
import sqlite3

from Exp_db_to_Excel import Exp_db_to_Excel
from Summarize_db import Summarize_db

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

# copy_db = r"D:\Agent\Database\Chrome_copy.db"
chrome_db = Path(r"D:\Agent\Database\Chrome_db.db")
copy_db = Path(r"D:\Agent\Database\Chrome_copy.db")

shutil.copy2(history_db, copy_db)
print("Chrome history copied")

# Load all visited URLs into a set
# conn = sqlite3.connect(copy_db)
conn = sqlite3.connect(copy_db)
cursor = conn.cursor()

# Create a new table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS visited_urls (
        url TEXT PRIMARY KEY,
        visited_at TEXT
    )
""")

# end_count = Summarize_db(copy_db,"visited_urls","")
end_count = Summarize_db(copy_db, "urls", "")

# Chrome stores timestamps as microseconds since 1601-01-01 UTC
cursor.execute("""
    INSERT OR REPLACE INTO visited_urls (url, visited_at)
    SELECT
        url,
        datetime(last_visit_time / 1000000 - 11644473600, 'unixepoch')
    FROM urls
    WHERE strftime('%Y', visited_at) = '2026'
    --WHERE last_visit_time > 0
""")

conn.commit()
conn.close()

# end_count = Summarize_db(copy_db,"visited_urls","")
end_count = Summarize_db(copy_db, "visited_urls", "")

Exp_db_to_Excel(copy_db,"visited_urls","(new)","")

# Example:
# if job["url"] in visited_urls:
#     print("Already visited")