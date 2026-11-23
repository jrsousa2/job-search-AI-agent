import pandas as pd
from pathlib import Path

folder = Path(r"D:\Agent\History")
output = r"D:\Agent\All.xlsx"

files = [
    f for f in folder.glob("*.xlsx")
    if f.name.lower() != "all.xlsx"
]

df = pd.concat(
    [pd.read_excel(f) for f in files],
    ignore_index=True
)

df.to_excel(output, index=False)

print(f"Combined {len(files)} files into {output}")
print(f"Total rows: {len(df)}")