# Processed Data Documentation  
### Energy Economics Revision Project  
*Prepared by: Morgan Evans*  
*Updated: October 2025*

---

## Overview
This folder contains all processed, state-year datasets used to extend the Energy Economics analysis through 2023.

---

## 1. Energy Data

| **Headers**                                                                                                                                                                              | **File Name** | **Description** | **Source** | **Years** | **State Format** |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|------------------|-------------|-------------|------------------|
| year, state, coal, natural_gas, nuclear, hydro, wind, solar, oil, biomass, wood, geothermal, other, other_gases, pumped_storage, total                                                   | `generation_shares_wide.csv` | State-level generation shares (% of total generation) by fuel type. Each row = (state, year). | EIA Form 923 | 1990–2023 | **Full names** |
| year, state, all_sources, bio_cap, coal_cap, geotherm_cap, hydro_cap, ng_cap, nuclear_cap, oil_cap, other_cap, other_gases_cap, pumped storage, solar thermal and photovoltaic, wind_cap | `generation_capacity_wide.csv` | Nameplate capacity (MW) by energy source. Represents installed generation capacity, not actual output. | EIA Form 860 | 1990–2023 | **Full names** |
| year, abbrev, sales_MWH, log_sales, price, log_price                                                                                                                                     | `electricity_sales.csv` | Annual average retail electricity price (cents/kWh) for total electric industry. Computed from total revenue ÷ total sales (MWh). | EIA Form 861 | 1990–2023 | **Abbreviations** |
| year, state, price                                                                                                                                                                       | `natgas_price.csv` | State-level natural gas price (USD per thousand cubic feet). | EIA Natural Gas Data Browser (Forms 176, 857, 191) | 1990–2023 | **Full names** |
| state, year, generation_mwh, generation_adj_mwh, estcb_mwh, energy_exports_mwh, percent_energy_exports                                                                                   | `percent_energy_exports.csv` | Share of electricity generated minus consumed — proxy for energy exports (%). | Derived from EIA Forms 923, 861, and state consumption data | 1990–2023 | **Abbreviations** |

---

## 2. Economic & Demographic Data

| **Variable(s)** | **File Name** | **Description** | **Source** | **Years** | **State Format** |
|------------------|----------------|------------------|-------------|-----------|------------------|
| state, year, gsp_nominal, deflator, gsp_real | `gsp_real.csv` | Real Gross State Product (chained 2017 dollars). Log-transformed for regressions. | BEA Regional Economic Accounts | 1990–2023 | **Abbreviations** |
| state, year, population | `state_population.csv` | State population (annual). Used for population-weighted metrics and log transformation. | U.S. Census Bureau / BEA | 1990–2023 | **Abbreviations** |

---

## 3. Political & Policy Data

| **Variable(s)** | **File Name** | **Description** | **Source** | **Years** | **State Format** |
|------------------|----------------|------------------|-------------|-------------|------------------|
| state, year, govparty, legislature_control_DEM, legislature_control_GOP, net_meter, state_control_DEM, state_control_GOP | `politics_19_23.csv` | Governor and legislature party control. Unified control indicators mark single-party dominance. | Klarner Politics Dataset | 2019–2023 | **Full names** |

---

## 4. Weather Data

| **Variable(s)** | **File Name** | **Description** | **Source** | **Years** | **State Format** |
|------------------|----------------|------------------|-------------|-------------|------------------|
| state, year, cdd, hdd | `weather_data.csv` | Population-weighted annual Heating Degree Days (HDD) and Cooling Degree Days (CDD). Reflect climate-driven energy demand by state. | NOAA Climate Prediction Center / NCEI | 1990–2023 | **Abbreviations** |


---

## 5. Legacy / Non-Standardized Files

These files contain similar information to the standardized datasets above but were preserved for traceability and comparison.  
They generally maintain the same variable definitions but differ in formatting, structure (long vs. wide), or level of processing.

| **File Name** | **Description** | **Relation to Processed File** | **Format** | **State Format** | **Years** |
|----------------|----------------|--------------------------------|-------------|------------------|-----------|
| `generation_shares.csv` | Generation shares by state and fuel type, originally in long format with multiple records per (state, year). | Source for `generation_shares_wide.csv`. The wide version pivots fuel types into columns for easier regression use. | Long format | **Full names** | 1990–2023 |
| `generation_capacity.csv` | Generation capacity by state and energy source, non-wide version of installed capacity data. | Source for `generation_capacity_wide.csv`. Reformatted into wide structure to match standardized merge variables. | Long format | **Full names** | 1990–2023 |
| `gsp_nominal.csv` | Nominal Gross State Product (current dollars). | Source for `gsp_real.csv`. The processed version adds a deflator and computes real GSP (chained 2017 dollars). | Long format | **Abbreviations** | 1990–2023 |

**Note:** These non-standardized files are retained for reproducibility checks and should not be merged directly with other datasets without conversion to standardized naming and structure.
