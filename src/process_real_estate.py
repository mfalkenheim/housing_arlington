import os
import gzip
import pandas as pd
import requests
import matplotlib.pyplot as plt

PROP_URL = "https://download.data.arlingtonva.us/RealEstate/PropertyRedacted.txt"
ASSESS_URL = "https://download.data.arlingtonva.us/RealEstate/Assessment.txt.gz"

PROP_FILE = "PropertyRedacted.txt"
ASSESS_FILE = "Assessment.txt.gz"

def download_file(url, dest):
    if os.path.exists(dest):
        print(f"{dest} already exists. Skipping download.")
        return
    print(f"Downloading {url} to {dest}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {dest}.")

def main():
    download_file(PROP_URL, PROP_FILE)
    download_file(ASSESS_URL, ASSESS_FILE)

    print("Loading properties...")
    # Load all columns as str to avoid auto-boolean or float conversion issues
    prop_df = pd.read_csv(PROP_FILE, sep="|", dtype=str, low_memory=False)
    print(f"Loaded {len(prop_df)} properties.")

    # Filter to active properties to match official reports
    print("Filtering properties for active status...")
    prop_active = prop_df[
        (prop_df["ReasPropertyStatusCode"] == "A") & 
        (prop_df["PropertyExpiredInd"] == "False")
    ].copy()
    print(f"Filtered to {len(prop_active)} active properties.")

    print("Loading assessments...")
    # Load all columns as str
    assess_df = pd.read_csv(ASSESS_FILE, sep="|", dtype=str, low_memory=False)
    print(f"Loaded {len(assess_df)} assessments.")

    # Convert assessment date and extract year
    assess_df["AssessmentDate"] = pd.to_datetime(assess_df["AssessmentDate"], errors="coerce")
    assess_df["Year"] = assess_df["AssessmentDate"].dt.year
    assess_df["TotalValueAmt"] = pd.to_numeric(assess_df["TotalValueAmt"], errors="coerce")
    assess_df["AssessmentKey"] = pd.to_numeric(assess_df["AssessmentKey"], errors="coerce")

    # Deduplicate assessments: sort by AssessmentKey and keep last per Year + RPC
    print("Deduplicating assessments (keeping latest AssessmentKey per property per year)...")
    assess_sorted = assess_df.sort_values("AssessmentKey")
    assess_last = assess_sorted.drop_duplicates(subset=["Year", "RealEstatePropertyCode"], keep="last").copy()
    print(f"Deduplicated from {len(assess_df)} to {len(assess_last)} assessments.")

    # Merge properties and assessments
    print("Merging assessments with active property classifications...")
    merged = pd.merge(assess_last, prop_active[["RealEstatePropertyCode", "PropertyClassTypeCode", "PropertyClassTypeDsc"]], on="RealEstatePropertyCode", how="inner")
    print(f"Merged assessments count: {len(merged)}")

    # Classify based on approved mapping logic using first character/digit of PropertyClassTypeCode
    print("Classifying properties...")
    merged["FirstDigit"] = merged["PropertyClassTypeCode"].str[0]

    # Map to the four categories:
    # 1, 2, 4 -> Truly Commercial
    # 3 -> Rental Apartments
    # 6 -> Condominiums
    # 5 -> Other Residential
    
    category_map = {
        "1": "Truly Commercial",
        "2": "Truly Commercial",
        "4": "Truly Commercial",
        "3": "Rental Apartments",
        "6": "Condominiums",
        "5": "Other Residential"
    }
    
    merged["Category"] = merged["FirstDigit"].map(category_map)
    
    # Exclude unmatched (NaN) or other codes (like 700s) from the official split to align with reports
    df_valid = merged[merged["Category"].notna()].copy()
    print(f"Valid classified assessments count: {len(df_valid)}")

    # Aggregate Total Assessed Value by Year and Category
    print("Aggregating total assessed values by year and category...")
    pivot_df = df_valid.groupby(["Year", "Category"])["TotalValueAmt"].sum().unstack(fill_value=0)

    # Ensure all four categories exist in the columns
    for col in ["Truly Commercial", "Rental Apartments", "Condominiums", "Other Residential"]:
        if col not in pivot_df.columns:
            pivot_df[col] = 0.0

    # Sort columns for consistency
    pivot_df = pivot_df[["Truly Commercial", "Rental Apartments", "Condominiums", "Other Residential"]]

    # Compute comparison metrics
    pivot_df["Official Commercial"] = pivot_df["Truly Commercial"] + pivot_df["Rental Apartments"]
    pivot_df["Official Residential"] = pivot_df["Condominiums"] + pivot_df["Other Residential"]
    pivot_df["Total Official Base"] = pivot_df["Official Commercial"] + pivot_df["Official Residential"]

    pivot_df["Official Commercial Share (%)"] = (pivot_df["Official Commercial"] / pivot_df["Total Official Base"]) * 100
    pivot_df["Official Residential Share (%)"] = (pivot_df["Official Residential"] / pivot_df["Total Official Base"]) * 100
    
    pivot_df["Truly Commercial Share (%)"] = (pivot_df["Truly Commercial"] / pivot_df["Total Official Base"]) * 100
    pivot_df["Rental Apartments Share (%)"] = (pivot_df["Rental Apartments"] / pivot_df["Total Official Base"]) * 100
    pivot_df["Condominiums Share (%)"] = (pivot_df["Condominiums"] / pivot_df["Total Official Base"]) * 100
    pivot_df["Other Residential Share (%)"] = (pivot_df["Other Residential"] / pivot_df["Total Official Base"]) * 100

    # Filter to display/save robust years (e.g. 2000 to 2026)
    pivot_df = pivot_df.loc[pivot_df.index >= 2000]

    # Save to CSV
    csv_filename = "assessment_comparison.csv"
    pivot_df.to_csv(csv_filename)
    print(f"Saved comparison summary to {csv_filename}.")

    # Generate Chart
    print("Generating line chart contrasting commercial shares...")
    plt.figure(figsize=(10, 6))
    plt.plot(pivot_df.index.to_numpy(), pivot_df["Official Commercial Share (%)"].to_numpy(), marker="o", linewidth=2.5, color="#1f77b4", label="Official Commercial Share (Incl. Multi-Family Rentals)")
    plt.plot(pivot_df.index.to_numpy(), pivot_df["Truly Commercial Share (%)"].to_numpy(), marker="s", linewidth=2.5, color="#d62728", label="Truly Commercial Share (Excl. Multi-Family Rentals)")
    
    plt.title("Arlington County Real Estate Assessment: Official vs. Truly Commercial Share (2000-2026)", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Year", fontsize=11, labelpad=10)
    plt.ylabel("Share of Total Assessment (%)", fontsize=11, labelpad=10)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xticks(pivot_df.index[::2].to_numpy(), rotation=45)
    plt.ylim(0, 100 if pivot_df["Official Commercial Share (%)"].max() <= 100 else None)
    plt.legend(fontsize=10, loc="best")
    plt.tight_layout()

    chart_filename = "commercial_share_chart.png"
    plt.savefig(chart_filename, dpi=150)
    print(f"Generated chart and saved to {chart_filename}.")

    # Print summary table for recent years
    print("\n" + "="*80)
    print("SUMMARY COMPARISON TABLE (Recent Years, $ Billions)")
    print("="*80)
    summary_cols = [
        "Official Commercial", "Official Residential", "Total Official Base",
        "Official Commercial Share (%)", "Truly Commercial Share (%)", "Rental Apartments Share (%)"
    ]
    pd.set_option('display.max_columns', None)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    
    print_df = pivot_df[summary_cols].copy()
    print_df["Official Commercial"] /= 1e9
    print_df["Official Residential"] /= 1e9
    print_df["Total Official Base"] /= 1e9
    
    print_df = print_df.rename(columns={
        "Official Commercial": "Off. Comm ($B)",
        "Official Residential": "Off. Res ($B)",
        "Total Official Base": "Total ($B)",
        "Official Commercial Share (%)": "Off. Comm Share (%)",
        "Truly Commercial Share (%)": "Truly Comm Share (%)",
        "Rental Apartments Share (%)": "Rental Apt Share (%)"
    })
    print(print_df.tail(15))
    print("="*80)

if __name__ == "__main__":
    main()