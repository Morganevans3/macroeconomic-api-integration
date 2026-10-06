import requests
import pandas as pd

API_KEY = "9mICKH1LdGnZ7PVX6hMSTM35Cqpd85mmKYX1cjfn"
BASE_URL = "https://api.eia.gov/v2/seriesid/"

# Expanded and corrected fuel mapping
fuels = {
    "coal": ["COW"],
    "natgas": ["NG"],
    "nuclear": ["NUC"],
    "hydro": ["HYC", "HPS"],  # Conventional + Pumped Storage
    "wind": ["WND"],
    "solar": ["SUN"],
    "biomass": ["OBIO", "WWW"],  # Other + Wood biomass
    "geothermal": ["GEO"],
    "oil": ["OIL", "PEL", "PCO"]  # Combine all oil types
}

states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM",
    "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY"
]

all_data = []
missing_series = []

for fuel_name, fuel_codes in fuels.items():
    for state in states:
        combined_df = pd.DataFrame()

        for code in fuel_codes:
            sid = f"ELEC.GEN.{code}-{state}-99.A"
            url = f"{BASE_URL}{sid}?api_key={API_KEY}"
            resp = requests.get(url).json()

            if "response" in resp and "data" in resp["response"]:
                df = pd.DataFrame(resp["response"]["data"])
                if not df.empty and "generation" in df.columns:
                    df["generation"] = pd.to_numeric(df["generation"], errors="coerce")
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                else:
                    missing_series.append(sid)
            else:
                missing_series.append(sid)

        if not combined_df.empty:
            # Group by year, sum generation across sub-codes
            combined_df = combined_df.groupby("period", as_index=False)["generation"].sum()
            combined_df["fuel"] = fuel_name
            combined_df["state"] = state
            combined_df.rename(columns={"period": "year"}, inplace=True)
            all_data.append(combined_df)
            print(f"✅ Added {fuel_name} for {state} ({len(combined_df)} rows)")
        else:
            print(f"⚠️ No data for {fuel_name} in {state}")

# Combine all results
df_all = pd.concat(all_data, ignore_index=True)

# Convert year and generation to numeric
df_all["year"] = pd.to_numeric(df_all["year"], errors="coerce")
df_all["generation"] = pd.to_numeric(df_all["generation"], errors="coerce")

# Save
output_path = "../../Data/New/generation/EIA_generation_full_fixed.csv"
df_all.to_csv(output_path, index=False)
print(f"\n✅ Saved full dataset to {output_path}")

# Log missing series
if missing_series:
    with open("../../Data/New/missing_series_log.txt", "w") as f:
        for sid in missing_series:
            f.write(sid + "\n")
    print(f"⚠️ Logged {len(missing_series)} missing series to missing_series_log.txt")
