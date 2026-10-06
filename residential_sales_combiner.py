# append_elec_sales.py
import pandas as pd
import numpy as np

# File paths
MAIN_FILE = "../../Data/New/sales/EIA_electricity_sales_full.csv"
SALES22 = "../Data/New/table2_22.csv"
SALES23 = "../Data/New/table2_23.csv"
OUTPUT = "../Data/New/EIA_electricity_sales_full.csv"

# Load main dataset
df = pd.read_csv(MAIN_FILE)

# Load new sales files
def load_sales(file, year, state_abbrev, scale_thousands=False):
    s = pd.read_csv(file)
    s = s[["State", "Total"]].copy()

    # remove commas and convert to numeric
    s["Total"] = s["Total"].astype(str).str.replace(",", "")
    s["sales_MWH"] = pd.to_numeric(s["Total"], errors="coerce")

    # ⚠️ Fix 2022 if numbers are in thousands → scale up
    if scale_thousands:
        s["sales_MWH"] = s["sales_MWH"] * 1000

    # Map state abbrev
    s["abbrev"] = s["State"].map(state_abbrev)
    s["year"] = year
    return s[["year", "abbrev", "sales_MWH"]]

# State name → abbrev map
state_abbrev = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
    "Colorado":"CO","Connecticut":"CT","Delaware":"DE","District of Columbia":"DC",
    "Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL",
    "Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA",
    "Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN",
    "Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV",
    "New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY",
    "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR",
    "Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD",
    "Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA",
    "Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
}

# Load cleaned 2022 + 2023 sales
s22 = load_sales(SALES22, 2022, state_abbrev, scale_thousands=True)  # ⚠️ adjust if 2022 is in thousands
s23 = load_sales(SALES23, 2023, state_abbrev)

sales_new = pd.concat([s22, s23], ignore_index=True)

# Merge: update missing sales_MWH in df
df = df.merge(sales_new, on=["year","abbrev"], how="left", suffixes=("", "_new"))

# Fill missing sales_MWH/log_sales with new values
df["sales_MWH"] = df["sales_MWH"].fillna(df["sales_MWH_new"])
df["log_sales"] = np.where(
    df["sales_MWH"].notna(),
    np.log(df["sales_MWH"]),
    df["log_sales"]
)

# Drop helper column
df = df.drop(columns=["sales_MWH_new"])

# Save
df.to_csv(OUTPUT, index=False)
print("✅ Updated dataset with sales_MWH + log_sales for 2022–2023")
print("Years covered:", int(df['year'].min()), "-", int(df['year'].max()))

# 🔎 Sanity check
print("\nSanity check (mean sales_MWH by year, last 5 years):")
print(df.groupby("year")["sales_MWH"].mean().tail(5))
