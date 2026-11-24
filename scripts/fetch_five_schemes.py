
import requests
import pandas as pd
from pathlib import Path

# Project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Verified scheme details
SCHEMES = {
    "SBI": {
        "code": "119598",
        "fund_house": "SBI Mutual Fund",
        "keyword": "SBI LARGE CAP",
        "filename": "sbi_bluechip_live_nav.csv",
    },
    "ICICI": {
        "code": "120586",
        "fund_house": "ICICI Prudential Mutual Fund",
        "keyword": "ICICI PRUDENTIAL LARGE CAP",
        "filename": "icici_bluechip_live_nav.csv",
    },
    "Nippon": {
        "code": "118632",
        "fund_house": "Nippon India Mutual Fund",
        "keyword": "NIPPON INDIA LARGE CAP",
        "filename": "nippon_large_cap_live_nav.csv",
    },
    "Axis": {
        "code": "120465",
        "fund_house": "Axis Mutual Fund",
        "keyword": "AXIS LARGE CAP",
        "filename": "axis_bluechip_live_nav.csv",
    },
    "Kotak": {
        "code": "120152",
        "fund_house": "Kotak Mahindra Mutual Fund",
        "keyword": "KOTAK LARGE CAP",
        "filename": "kotak_bluechip_live_nav.csv",
    },
}


def fetch_scheme(name, details):
    code = details["code"]
    url = f"https://api.mfapi.in/mf/{code}"

    print(f"\nFetching {name}...")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    result = response.json()
    metadata = result["meta"]

    # Validate fund house
    if metadata["fund_house"] != details["fund_house"]:
        raise ValueError(
            f"{name}: Unexpected fund house: "
            f"{metadata['fund_house']}"
        )

    # Validate scheme name
    scheme_name = metadata["scheme_name"].upper()

    if details["keyword"] not in scheme_name:
        raise ValueError(
            f"{name}: Unexpected scheme name: "
            f"{metadata['scheme_name']}"
        )

    # Convert API data into a DataFrame
    df = pd.DataFrame(result["data"])

    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["date"] = pd.to_datetime(
        df["date"],
        format="%d-%m-%Y",
        errors="coerce"
    )

    df = df.dropna(subset=["date", "nav"])

    # Add scheme information
    df["scheme_code"] = code
    df["scheme_name"] = metadata["scheme_name"]
    df["fund_house"] = metadata["fund_house"]

    return df


def main():
    print("=" * 55)
    print("FIVE MUTUAL FUND NAV DATA FETCHER")
    print("=" * 55)

    # Fetch and validate all schemes before saving
    fetched_data = {}

    for name, details in SCHEMES.items():
        fetched_data[name] = fetch_scheme(name, details)

    print("\nAll five schemes verified successfully.")
    print("\nSaving NAV files...")

    for name, df in fetched_data.items():
        filename = SCHEMES[name]["filename"]
        output_path = RAW_DIR / filename

        df.to_csv(output_path, index=False)

        print(f"\n{name}")
        print(f"Records: {len(df)}")
        print(f"Saved: {output_path}")

    print("\n" + "=" * 55)
    print("ALL FIVE NAV FILES SAVED SUCCESSFULLY")
    print("=" * 55)


if __name__ == "__main__":
    main()