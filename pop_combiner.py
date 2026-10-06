'''
Combine state populations of 1990-2018 and then new downloaded data 2019-2023
new data (2019-2023) = ../Data/New/state_pop_19_23.csv
header is state,year,population but state is abbrev

old data (1990-2018) = ../Data/pop1990-2018byyear.csv
the format is just states as headers and it is full names
and each row is just the population no years

https://www.census.gov/data/tables/time-series/demo/popest/2020s-state-total.html

there is a github to fork - https://github.com/JoshData/historical-state-population-csv

I ran tests to ensure the population per state is accurate and had a check of if the data
between 2018 and 2019 increased by more than 2% which did not happen

Also there was not DC for 1990-2018 but i kept the 2019-2023 DC pop data
'''

import pandas as pd
from pathlib import Path

NAME_TO_ABBR = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO",
    "Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID",
    "Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA",
    "Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN",
    "Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH",
    "New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND",
    "Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
    "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA",
    "Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY","District of Columbia":"DC"
}
ABBR_TO_NAME = {v: k for k, v in NAME_TO_ABBR.items()}

def combine_state_populations(
    old_wide_path="../Data/pop1990-2018byyear.csv",
    new_tidy_path="../Data/New/state_pop_19_23.csv",
    out_path="../Data/state_population.csv",
    old_start_year=1990,
    old_end_year=2018,
    enforce_expected_counts=True,   # set False to only warn
):
    """
    Combine state populations of 1990–2018 (wide; full state names as columns, rows in year order, no 'year' col)
    with 2019–2023 (tidy; columns = state (USPS abbr), year, population).

    Adapts expected state coverage per year to what each source actually includes (e.g., if DC is missing in old file).
    """
    old_wide_path = Path(old_wide_path)
    new_tidy_path = Path(new_tidy_path)
    out_path = Path(out_path)

    # -------------------------
    # Load & reshape OLD wide (1990–2018)
    # -------------------------
    old_df = pd.read_csv(old_wide_path)

    expected_rows = old_end_year - old_start_year + 1
    if len(old_df) != expected_rows:
        raise ValueError(
            f"Old file rows ({len(old_df)}) do not match expected {old_start_year}..{old_end_year} ({expected_rows})."
        )

    # Ensure canonical column names (strip accidental whitespace)
    old_df = old_df.rename(columns={c: c.strip() for c in old_df.columns})
    old_df.insert(0, "year", list(range(old_start_year, old_end_year + 1)))

    # Identify state columns (everything except 'year')
    state_cols = [c for c in old_df.columns if c != "year"]

    # Check that all old-file state columns are known full names
    unknown_cols = [c for c in state_cols if c not in NAME_TO_ABBR]
    if unknown_cols:
        raise ValueError(
            "Old file has columns that are not recognized full state names (incl. DC): "
            + ", ".join(unknown_cols)
        )

    # Map the old-file state set to USPS abbrs (this may be 50 if DC is missing)
    old_states_abbr = {NAME_TO_ABBR[c] for c in state_cols}

    # Melt to tidy: (year, state_full, population) -> (state, year, population)
    old_long = old_df.melt(id_vars="year", value_vars=state_cols,
                           var_name="state_full", value_name="population")

    # Clean numeric populations (remove commas, coerce)
    old_long["population"] = (
        old_long["population"].astype(str).str.replace(",", "", regex=False).str.strip()
    )
    old_long["population"] = pd.to_numeric(old_long["population"], errors="coerce")
    if old_long["population"].isna().any():
        bad = old_long[old_long["population"].isna()].head(5)
        raise ValueError(f"Found non-numeric population values in old file (sample):\n{bad}")

    old_long["state"] = old_long["state_full"].map(NAME_TO_ABBR)
    if old_long["state"].isna().any():
        bad_states = old_long[old_long["state"].isna()]["state_full"].unique()
        raise ValueError("Some old-file state columns could not be mapped to USPS abbreviations: "
                         + ", ".join(bad_states))

    old_tidy = old_long[["state", "year", "population"]].copy()
    old_tidy["state"] = old_tidy["state"].str.upper()

    # -------------------------
    # Load NEW tidy (2019–2023)
    # -------------------------
    new_tidy = pd.read_csv(new_tidy_path)
    required_cols = {"state", "year", "population"}
    if not required_cols.issubset(new_tidy.columns):
        raise ValueError(f"New file must have columns {required_cols}, got {list(new_tidy.columns)}")

    new_tidy = new_tidy[list(required_cols)].copy()
    new_tidy["state"] = new_tidy["state"].str.upper().str.strip()
    new_tidy["year"] = pd.to_numeric(new_tidy["year"], errors="raise", downcast="integer")
    new_tidy["population"] = pd.to_numeric(new_tidy["population"], errors="raise")

    # Validate new-file abbreviations
    valid_abbrs = set(ABBR_TO_NAME)
    bad_abbrs = sorted(set(new_tidy["state"]) - valid_abbrs)
    if bad_abbrs:
        raise ValueError("New file has unknown state abbreviations: " + ", ".join(bad_abbrs))

    new_states_abbr = set(new_tidy["state"].unique())
    new_years = sorted(new_tidy["year"].unique())

    # -------------------------
    # Combine & sort
    # -------------------------
    combined = pd.concat([old_tidy, new_tidy], ignore_index=True)
    combined["year"] = combined["year"].astype(int)
    combined["population"] = combined["population"].astype(int)
    combined.sort_values(["state", "year"], inplace=True)
    combined = combined.drop_duplicates(subset=["state", "year"], keep="last")

    # -------------------------
    # Per-year expected-state validation
    # -------------------------
    # Build expected state set per year based on source coverage
    year_expected_states = {}
    for y in range(old_start_year, old_end_year + 1):
        year_expected_states[y] = set(old_states_abbr)  # whatever the old file actually had
    for y in new_years:
        year_expected_states[y] = set(new_states_abbr)  # whatever the new file actually has

    problems = {}
    for y, expected in year_expected_states.items():
        present = set(combined.loc[combined["year"] == y, "state"])
        missing = sorted(expected - present)
        extra = sorted(present - expected)
        if missing or extra:
            problems[y] = {
                "expected_count": len(expected),
                "present_count": len(present),
                "missing": missing,
                "extra": extra,
            }

    if problems:
        # Make a readable summary
        lines = []
        for y in sorted(problems):
            p = problems[y]
            msg = (f"{y}: present={p['present_count']} expected={p['expected_count']}"
                   f"{' | missing='+', '.join(p['missing']) if p['missing'] else ''}"
                   f"{' | extra='+', '.join(p['extra']) if p['extra'] else ''}")
            lines.append(msg)
        summary = "\n".join(lines)
        if enforce_expected_counts:
            raise ValueError("State coverage mismatches by year:\n" + summary)
        else:
            print("WARNING: State coverage mismatches by year:\n" + summary)

    # Basic sanity
    if (combined["population"] < 0).any():
        raise ValueError("Found negative population values, which is invalid.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(out_path, index=False)
    return combined


if __name__ == "__main__":
    df = combine_state_populations(
        old_wide_path="../../Data/pop1990-2018byyear.csv",
        new_tidy_path="../../Data/New/population/state_pop_19_23.csv",
        out_path="../../Data/New/population/state_pop_1990_2023.csv",
        old_start_year=1990,
        old_end_year=2018
    )
    print(df.head())
    print(df.tail())




