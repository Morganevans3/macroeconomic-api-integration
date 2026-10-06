'''

takes the gas prices csv file and creates a new csv file with correct structure

'''
import pandas as pd

# Load file with both header rows
file_path = "../../Data/New/gas_price.csv"

# Read the file, keeping both headers
df = pd.read_csv(file_path, header=[0, 1])

# Fix the first column name
df.columns = df.columns.droplevel(0)
df = df.rename(columns={'Date': 'year'})

# Convert to long format
df_long = df.melt(id_vars=['year'], var_name='state_full', value_name='price')

# Extract state name (the text after "in " and before the parentheses)
df_long['state'] = (
    df_long['state_full']
    .str.extract(r'in\s+(.+?)\s*\(')[0]
    .fillna('U.S.')
    .replace({'the District of Columbia': 'District of Columbia'})
)

# Keep only needed columns
df_final = df_long[['year', 'state', 'price']]

# Convert year column to integer if possible (drop non-numeric)
df_final = df_final[pd.to_numeric(df_final['year'], errors='coerce').notnull()]
df_final['year'] = df_final['year'].astype(int)

# Sort and clean
df_final = df_final.sort_values(['state', 'year']).reset_index(drop=True)

# Save output
df_final.to_csv('../Data/New/natgas_price.csv', index=False)

print(df_final.head())


