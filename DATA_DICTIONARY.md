# Data Dictionary

## Source Dataset

Monthly public transport patronage by mode, published by the Department of Transport and Planning / DataVic.

## Grain

One row per calendar month in the raw file, with separate columns for each public transport mode.

The analytical long table uses one row per month and mode.

## Core Fields

| Field | Type | Description |
|---|---:|---|
| `date` | date | First day of the month generated from `year` and `month`. |
| `year` | integer | Calendar year. |
| `month` | integer | Calendar month number. |
| `month_name` | text | Month name from the source data. |
| `mode` | text | Public transport mode. |
| `patronage` | integer | Monthly patronage count for the mode. |
| `network_group` | text | Derived grouping: Metropolitan or Regional/VLine. |

## Modes

- Metropolitan Train
- Metropolitan Tram
- Metropolitan Bus
- V/Line Train
- V/Line Coach
- Regional Bus

## Derived Metrics

| Metric | Definition |
|---|---|
| Annual patronage | Sum of monthly patronage by calendar year and mode. |
| Total annual patronage | Sum of annual patronage across all modes. |
| Mode share | Mode annual patronage divided by total annual patronage for the same year. |
| Recovery percentage | Latest complete year patronage divided by 2019 baseline patronage. |
| Year-on-year change | Percentage change in total annual patronage from previous calendar year. |

## Data Quality Notes

- One source value in the raw CSV included extra text after a numeric value: `940930Jan-25`.
- The Python cleaning function extracts the leading numeric value and preserves it as `940930`.
- 2026 is year-to-date only in the downloaded file, so complete-year comparisons use 2025.

## Known Limitations

- Monthly mode-level patronage does not identify station, route, corridor, time-of-day or service-level drivers.
- Patronage data alone does not establish causation.
- Policy interpretation should be combined with service frequency, reliability, fare policy, population growth, land-use change, major project delivery and stakeholder evidence.

