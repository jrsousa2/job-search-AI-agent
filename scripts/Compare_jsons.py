# CHECK THAT MODIFIED JSON (ONE ENTRY PER LINE) IS NOT BROKEN
import json

def json_subset(file1, file2):
    with open(file1, "r", encoding="utf-8") as f:
        json1 = json.load(f)

    with open(file2, "r", encoding="utf-8") as f:
        json2 = json.load(f)

    missing = []

    for item in json1:
        if item not in json2:
            missing.append(item)

    if missing:
        print("The first JSON is NOT entirely contained in the second JSON.")
        print("\nMissing entries:")
        for item in missing:
            print(item)
        return False
    else:
        print("The first JSON is entirely contained in the second JSON.")
        return True


# Example
json_subset(r"D:\Agent\data\watchlist.json", r"D:\Agent\Bak\watchlist.json")