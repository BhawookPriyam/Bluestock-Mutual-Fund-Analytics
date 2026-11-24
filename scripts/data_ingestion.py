
import pandas as pd
from pathlib import Path

# Project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORT_DIR = PROJECT_DIR / "reports"

# Expected CSV filenames
csv_files = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

# Store loaded datasets
datasets = {}

print("=" * 70)
print("BLUESTOCK MUTUAL FUND DATA INGESTION")
print("=" * 70)

# Load all CSV files
for file_name in csv_files:

    file_path = RAW_DATA_DIR / file_name

    print(f"\n\n{'=' * 70}")
    print(f"DATASET: {file_name}")
    print("=" * 70)

    if not file_path.exists():
        print(f"ERROR: File not found: {file_name}")
        continue

    try:
        df = pd.read_csv(file_path)
        datasets[file_name] = df

        print("\nShape:")
        print(df.shape)

        print("\nData types:")
        print(df.dtypes)

        print("\nFirst 5 rows:")
        print(df.head())

        print("\nMissing values:")
        print(df.isnull().sum())

    except Exception as error:
        print(f"ERROR loading {file_name}: {error}")

# Data quality analysis
print("\n\n" + "=" * 70)
print("DATA QUALITY SUMMARY")
print("=" * 70)

quality_report = []

for name, df in datasets.items():

    quality_report.append({
        "dataset": name,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    })

quality_df = pd.DataFrame(quality_report)

print(quality_df.to_string(index=False))

# Create reports folder if needed
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Export data quality report
report_path = REPORT_DIR / "data_quality_report.csv"
quality_df.to_csv(report_path, index=False)

print("\n" + "=" * 70)
print("INGESTION COMPLETED")
print("=" * 70)

print(f"Successfully loaded {len(datasets)} out of {len(csv_files)} datasets.")
print(f"Data quality report saved at: {report_path}")