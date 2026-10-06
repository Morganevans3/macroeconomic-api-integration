'''
forked from JoshData on Github
updated to just download 2019-2023
'''

# Downloads historical population of the 50 states plus DC from the
# U.S. Census's Annual Estimates of the Population for the U.S. and
# States, and for Puerto Rico (http://www.census.gov/popest/) as
# published by the Federal Reserve Bank of St. Louis at
# https://fred.stlouisfed.org/release?rid=118 because fred.stlouisfed.org
# provides cleanly fetchable tables for 1900-2017. Unfortunately it
# does not include Puerto Rico's population.
#

import csv
import io
import os
import urllib.request

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(arg, *rest, **kwrest): return arg

states = [
    'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL',
    'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA',
    'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE',
    'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI',
    'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'
]

# Ensure output folder exists
os.makedirs("../../Data/New", exist_ok=True)
output_path = os.path.abspath("../../Data/New/population/state_pop_19_23.csv")

with open(output_path, "w", newline="") as f:
    W = csv.writer(f)
    W.writerow(["state", "year", "population"])

    for state in tqdm(states):
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={state}POP"
        resp = urllib.request.urlopen(url)
        for date, pop in csv.reader(io.TextIOWrapper(resp)):
            if date == "observation_date":
                continue
            if not date.endswith("-01-01"):
                continue
            year = int(date.replace("-01-01", ""))
            if 2019 <= year <= 2023:
                W.writerow([state, year, int(round(float(pop) * 1000))])

print(f"✅ File saved at: {output_path}")

