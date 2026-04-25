import pandas as pd

url = "https://www.data.jma.go.jp/stats/etrn/view/monthly_s3_en.php?block_no=47662&view=1"

tables = pd.read_html(url, flavor="lxml")

print(f"Number of tables: {len(tables)}")
print("\n▼ TABLE 0 ▼")
print(tables[0].head())
print("\n▼ TABLE 1 ▼")
print(tables[1].head())
print("\nTABLE 1 COLUMNS:")
print(tables[1].columns)