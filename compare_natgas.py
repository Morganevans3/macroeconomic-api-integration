import pandas as pd

# ---- Load both files ----
natgas = pd.read_csv("../../Data/New/natgas_price_full.csv")   # year,state,price
other = pd.read_csv("../../Data/natgas_price.csv")               # date,Alabama,...

# ---- Clean column names ----
other.columns = other.columns.str.strip()  # remove spaces around names

# Detect the first column (usually 'date' or 'year')
first_col = other.columns[0]
print(f"Detected first column: {first_col}")

# Rename to 'year' for consistency
other = other.rename(columns={first_col: 'year'})

# ---- Reshape (wide → long) ----
other_long = other.melt(id_vars=['year'], var_name='state', value_name='value')

# ---- Make sure types match ----
natgas['year'] = natgas['year'].astype(int)
other_long['year'] = pd.to_numeric(other_long['year'], errors='coerce').astype('Int64')

# ---- Merge and compare ----
merged = pd.merge(natgas, other_long, on=['year', 'state'], how='inner')

merged['difference'] = merged['price'] - merged['value']
merged['match'] = merged['difference'].abs() < 0.01   # ignore tiny rounding

# ---- Filter mismatches ----
mismatches = merged[~merged['match']].copy()

# ---- Print results ----
if mismatches.empty:
    print("✅ All values match between files!")
else:
    print(f"⚠️ Found {len(mismatches)} mismatches:")
    print(mismatches[['year', 'state', 'price', 'value', 'difference']].to_string(index=False))
    mismatches.to_csv("mismatches_only.csv", index=False)
    print("\nSaved mismatches to mismatches_only.csv")

