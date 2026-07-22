# TRYING TO READ THE CHROME DB WITHOUT COPYING IT FIRST
# IT DOESN'T WORK BC CHROME DOESN'T ALLOW ACCESS TO THE DATABASE
from pathlib import Path
import sqlite3


from Summarize_db import Summarize_db
from Exp_db_to_Excel import Exp_db_to_Excel

# KILL ALL CHROME INSTANCES
# import subprocess
# subprocess.run("taskkill /F /IM chrome.exe", shell=True)
# subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"])


# Chrome History database (SOURCE - read only)
chrome_history_db = (
    Path.home()
    / "AppData"
    / "Local"
    / "Google"
    / "Chrome"
    / "User Data"
    / "Default"
    / "History"
)

# Your SQLite database (DESTINATION)
my_db = r"D:\Agent\Database\Chrome.db"


# Connect to your database (creates it if it does not exist)
conn = sqlite3.connect(my_db)
cursor = conn.cursor()


# Create destination table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS visited_urls (
        url TEXT PRIMARY KEY,
        visited_at TEXT
    )
""")


# Attach Chrome's database as another database
cursor.execute("""
    ATTACH DATABASE ? AS chrome_history
""", (str(chrome_history_db),))


# Copy Chrome history into your table
cursor.execute("""
    INSERT OR REPLACE INTO visited_urls (url, visited_at)
    SELECT
        url,
        datetime(last_visit_time / 1000000 - 11644473600, 'unixepoch')
    FROM chrome_history.urls
    WHERE last_visit_time > 0
""")


# Detach Chrome database
cursor.execute("""
    DETACH DATABASE chrome_history
""")


conn.commit()
conn.close()


end_count = Summarize_db(my_db, "visited_urls", "")

# Exp_db_to_Excel(my_db, "visited_urls", "", "")