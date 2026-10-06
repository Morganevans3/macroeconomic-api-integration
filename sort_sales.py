'''
sorts the EIA electricity sales by state and then by year
'''

import pandas as pd

# Load the CSV file
df = pd.read_csv("../../Data/New/sales/EIA_electricity_sales_full.csv")

# Sort by state and year
df_sorted = df.sort_values(by=["abbrev", "year"])

# Save to a new CSV file
df_sorted.to_csv("../Data/New/electricity_sales.csv", index=False)

print("File sorted and saved as electricity_sales.csv")