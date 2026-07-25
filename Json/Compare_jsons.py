# CHECK THAT MODIFIED JSON (ONE ENTRY PER LINE) IS NOT BROKEN
# CHECKS IF THE FIRST JSON IS A SUBSET OF THE SECOND
import json

# ADD SUBOLDER scripts
from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# MY FUNCTIONS IN scripts
from print_to_log import print_to_log

def json_subset(file1, file2, log_file):
    with open(file1, "r", encoding="utf-8") as f:
        json1 = json.load(f)

    with open(file2, "r", encoding="utf-8") as f:
        json2 = json.load(f)

    # USE ONLY PLATFORM AND SLUG TO COMPARE:
    # COMPREHENSION SET
    keys2 = {(item["platform"], item["slug"]) for item in json2}

    missing = []

    for item in json1:
        if (item["platform"], item["slug"]) not in keys2:
            missing.append(item)

    # STATS
    print(f"Entries in first JSON: {len(json1):,}")
    print(f"Entries in second JSON: {len(json2):,}")
    print(f"Entries in first JSON not in second: {len(missing):,}")

    if missing:
        print("The first JSON is NOT entirely contained in the second JSON.")
        print("\nMissing entries:", len(missing))
        # PRINTS RESULTS TO LOG FILE AS WELL
        for i, item in enumerate(missing):
            print_to_log(log_file,"Item {} of {}: {}\n",i,len(missing),item)
        #     print(item)
        return False
    else:
        print("The first JSON is entirely contained in the second JSON.")
        return True

# Example
json_subset(r"D:\Agent\Json\watchlist.json", r"D:\Agent\data\watchlist.json", r"D:\Agent\Logs\Diff_WL_entries.txt")