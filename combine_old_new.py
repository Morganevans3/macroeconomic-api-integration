import pandas as pd

# ---- File paths ----
file_old = "../../Code_and_Data_summary/EIA_generation_annual.csv"          # historical data (through ~2021)
file_new = "../../Data/New/generation/EIA_generation_full_fixed.csv"        # corrected new data (2018–2023)
file_out = "../../Data/New/generation/EIA_generation_combined.csv"

# ---- Load files ----
df_old = pd.read_csv(file_old)
df_new = pd.read_csv(file_new)

# ---- Clean & standardize old data ----
# Keep only "Total Electric Power Industry"
if "Producer" in df_old.columns:
    df_old = df_old[df_old["Producer"].str.contains("Total Electric Power Industry", case=False, na=False)]

# Rename columns to match new format
df_old = df_old.rename(columns={
    "abbrev": "state",
    "Fuel": "fuel",
    "Generation": "generation"
})
df_old = df_old[["year", "state", "fuel", "generation"]]

# ---- Clean & standardize new data ----
# Keep only relevant columns
df_new = df_new[["year", "state", "fuel", "generation"]]

# ---- Make sure both have consistent case/format ----
df_old["state"] = df_old["state"].str.strip().str.upper()
df_new["state"] = df_new["state"].str.strip().str.upper()
df_old["fuel"] = df_old["fuel"].str.strip().str.lower()
df_new["fuel"] = df_new["fuel"].str.strip().str.lower()

# ---- Check year coverage ----
print(f"Old data covers years {df_old['year'].min()}–{df_old['year'].max()}")
print(f"New data covers years {df_new['year'].min()}–{df_new['year'].max()}")

# ---- Identify overlap ----
years_old = set(df_old["year"].unique())
years_new = set(df_new["year"].unique())

# Prefer old data when overlapping, but fill missing combinations from new
if not years_old.isdisjoint(years_new):
    print(f"⚠️ Overlapping years detected: {sorted(years_old & years_new)}")

# Merge logic:
# 1️⃣ Start with all old data
df_combined = df_old.copy()

# 2️⃣ Find records in new that are missing from old (year,state,fuel)
old_keys = set(zip(df_old["year"], df_old["state"], df_old["fuel"]))
new_rows_needed = df_new[~df_new.apply(lambda r: (r["year"], r["state"], r["fuel"]) in old_keys, axis=1)]

# 3️⃣ Append those new rows
df_combined = pd.concat([df_combined, new_rows_needed], ignore_index=True)

# 4️⃣ Group to ensure uniqueness
df_combined = df_combined.groupby(["year", "state", "fuel"], as_index=False)["generation"].sum()

# ---- Replace negative generation values with 0 ----
df_combined["generation"] = pd.to_numeric(df_combined["generation"], errors="coerce").clip(lower=0)

# ---- Sort neatly ----
df_combined = df_combined.sort_values(["year", "state", "fuel"]).reset_index(drop=True)

# ---- Save final combined dataset ----
df_combined.to_csv(file_out, index=False)
print(f"✅ Combined dataset saved to {file_out}")
print(f"Total records: {len(df_combined):,}")
