
import requests
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

# Verified MFAPI scheme code
SCHEME_CODE = "119018"
API_URL = f"https://api.mfapi.in/mf/{SCHEME_CODE}"

print("Fetching HDFC Large Cap Fund NAV data...")
print("Scheme Code:", SCHEME_CODE)

try:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()
    meta = data.get("meta", {})

    fund_house = meta.get("fund_house", "")
    scheme_name = meta.get("scheme_name", "")

    # Validate the scheme before saving
    if "HDFC" not in fund_house.upper():
        raise ValueError(
            f"Wrong fund house returned: {fund_house}"
        )

    if "LARGE CAP" not in scheme_name.upper():
        raise ValueError(
            f"Unexpected scheme returned: {scheme_name}"
        )

    nav_records = data.get("data", [])

    if not nav_records:
        raise ValueError("No NAV records returned.")

    nav_df = pd.DataFrame(nav_records)

    nav_df["scheme_code"] = SCHEME_CODE
    nav_df["scheme_name"] = scheme_name
    nav_df["nav"] = pd.to_numeric(
        nav_df["nav"], errors="coerce"
    )
    nav_df["date"] = pd.to_datetime(
        nav_df["date"],
        format="%d-%m-%Y",
        errors="coerce"
    )

    nav_df = nav_df.dropna(subset=["date", "nav"])

    output_file = RAW_DATA_DIR / "hdfc_top_100_live_nav.csv"
    nav_df.to_csv(output_file, index=False)

    print("\nNAV FETCH SUCCESSFUL")
    print("-" * 50)
    print("Fund House:", fund_house)
    print("Scheme Name:", scheme_name)
    print("Scheme Code:", SCHEME_CODE)
    print("Total NAV Records:", len(nav_df))
    print("\nFirst 5 records:")
    print(nav_df.head())
    print("\nSaved to:", output_file)

except requests.exceptions.RequestException as error:
    print("\nAPI request failed:", error)

except (ValueError, KeyError) as error:
    print("\nData validation or processing failed:", error)