from pathlib import Path
import shutil
import sqlite3

from Exp_db_to_Excel import Exp_db_to_Excel
from Summarize_db import Summarize_db

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

chrome_db = Path(r"D:\Agent\Database\Chrome_db.db")
copy_db = Path(r"D:\Agent\Database\Chrome_copy.db")

def Chrome_db_hist():
    # CREATE COPY OF CHROME HISTORY
    shutil.copy2(history_db, copy_db)
    print("Chrome history copied")

    # CONNECT TO YOUR PERMANENT DB
    conn = sqlite3.connect(chrome_db)
    cursor = conn.cursor()

    # CREATE PERMANENT TABLE IF IT DOES NOT EXIST
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visited_urls (
            url TEXT PRIMARY KEY,
            visited_at TEXT
        )
    """)

    # ATTACH THE COPY OF CHROME DB
    cursor.execute("ATTACH DATABASE ? AS chrome_copy", (str(copy_db),))

    # INSERT NEW URLS FROM THE COPY INTO YOUR PERMANENT TABLE
    cursor.execute("""
        INSERT OR IGNORE INTO visited_urls (url, visited_at)
        SELECT
            url,
            datetime(last_visit_time / 1000000 - 11644473600, 'unixepoch')
        FROM chrome_copy.urls
        WHERE datetime(last_visit_time / 1000000 - 11644473600, 'unixepoch') >= '2026-07-01'
    """)
    
    # ROWS INSERTED
    print(f"New URLs inserted: {cursor.rowcount}")

    # COMMIT CHANGES
    conn.commit()
    # CLOSE CONNECTION
    conn.close()
    # DELETE TEMP DB
    copy_db.unlink()

    # ROW COUNT
    Summarize_db(chrome_db, "visited_urls", "")

# RUN THE CODE BELOW IF THE FILE IS MAIN
if __name__ == "__main__":
    # START
    Chrome_db_hist()

# Exp_db_to_Excel(chrome_db, "visited_urls", "(2)", "")