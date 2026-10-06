'''
the EIA generation data downloaded recently is in GWh instead of MWh so need to adjust by 1000
'''


import pandas as pd

# Load the generation file
df = pd.read_csv("../../Data/New/generation/EIA_generation_full.csv")

# Make a copy to avoid modifying in place
df_fixed = df.copy()

# Multiply generation values by 1000 for years 2022–2024
mask = df_fixed['year'].between(2022, 2024)
df_fixed.loc[mask, 'generation'] = df_fixed.loc[mask, 'generation'] * 1000

# Save to a new file
df_fixed.to_csv("../Data/New/EIA_generation_full.csv", index=False)

print("Conversion complete! Saved as EIA_generation_full_MWh.csv")
