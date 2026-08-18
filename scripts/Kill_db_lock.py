import os
import sys
import sqlite3
import subprocess
import time

JOBS_DB = r"D:\Agent\Database\jobs.db"


def unlock_database(db_path):
    # First test whether the database is currently locked.
    try:
        conn = sqlite3.connect(db_path, timeout=1)
        conn.execute("BEGIN IMMEDIATE")
        conn.rollback()
        conn.close()

        print("Database is not locked.")
        return True

    except sqlite3.OperationalError as e:
        if "locked" not in str(e).lower():
            print(f"SQLite error: {e}")
            return False

        print("Database is locked.")
        print("Looking for other Python processes...")

    # Get all Python processes except this process.
    current_pid = os.getpid()

    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True
    )

    pids = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        parts = line.split('","')
        if len(parts) >= 2:
            pid_text = parts[1].strip('"')

            try:
                pid = int(pid_text)
                if pid != current_pid:
                    pids.append(pid)
            except ValueError:
                pass

    if not pids:
        print("No other Python processes found.")
        return False

    print("Other Python processes found:")
    for pid in pids:
        print(f"  PID {pid}")

    # Terminate the other Python processes.
    for pid in pids:
        print(f"Terminating PID {pid}...")
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/F"],
            capture_output=True,
            text=True
        )

    # Give Windows a moment to release the file handles.
    time.sleep(1)

    # Test again.
    try:
        conn = sqlite3.connect(db_path, timeout=1)
        conn.execute("BEGIN IMMEDIATE")
        conn.rollback()
        conn.close()

        print("Database unlocked.")
        return True

    except sqlite3.OperationalError as e:
        print(f"Database is still locked: {e}")
        return False


if __name__ == "__main__":
    success = unlock_database(JOBS_DB)
    sys.exit(0 if success else 1)