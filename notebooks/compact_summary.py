from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = PROJECT_ROOT / "outputs" / "profiling"

files = [
    "dataset_inventory.csv",
    "schema_report.csv",
    "missingness_report.csv",
    "duplicate_report.csv",
]

for filename in files:
    path = PROFILE_DIR / filename

    print("\n")
    print("=" * 100)
    print(filename.upper())
    print("=" * 100)

    df = pd.read_csv(path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst rows:")
    print(df.head(30).to_string(index=False))
