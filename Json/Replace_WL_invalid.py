# REMOVES INVALID ENTRIES FROM WATCHLIST JSON
# REPLACE THE INVALID ENTRIES WITH FIXED ENTRIES
# PRINT STATS ABOUT INPUT AND OUTPUT
import json
# import config
import os
import datetime

# TODAY'S DATE
date_str = datetime.datetime.now().strftime("%Y-%m-%d")

input_json = os.path.join(r"D:\Agent\openroles", f"watchlist_source.json")
fixed_json = os.path.join(r"D:\Agent\openroles", "watchlist_fixes.json")
output_json = os.path.join(r"D:\Agent\openroles", f"watchlist.json")

# READ ORIGINAL WATCHLIST
with open(input_json, encoding="utf-8") as f:
    watchlist = json.load(f)

# ARE THERE DUPE COMPANIES?
Comps = [entry["company"].lower().strip() for entry in watchlist]
dist_comps = set(Comps)
print("List count:",len(Comps),"--Set count:",len(dist_comps),"\n")

# READ FIXED ENTRIES
with open(fixed_json, encoding="utf-8") as f:
    fixed_entries = json.load(f)

# INDEX FIXED ENTRIES BY COMPANY
fixed_lookup = {entry["company"]: entry for entry in fixed_entries}

# REPLACE ENTRIES
replaced = 0
new_watchlist = []

for entry in watchlist:
    company = entry["company"]
    if company in fixed_lookup:
        new_watchlist.append(fixed_lookup[company])
        replaced += 1
    else:
        new_watchlist.append(entry)

# WRITE ONE ENTRY PER LINE
with open(output_json, "w", encoding="utf-8") as f:
    f.write("[\n")
    for i, entry in enumerate(new_watchlist):
        json.dump(entry, f, ensure_ascii=False, separators=(",", ":"))
        if i < len(new_watchlist) - 1:
            f.write(",\n")
        else:
            f.write("\n")
    f.write("]\n")

# STATS
print(f"Input entries     : {len(watchlist)}")
print(f"Fixed entries     : {len(fixed_entries)}")
print(f"Entries replaced  : {replaced}")
print(f"Output entries    : {len(new_watchlist)}")
print(f"Saved to          : {output_json}")