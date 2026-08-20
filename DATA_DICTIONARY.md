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
| Baseline gap percentage | `100 - recovery_pct`. Positive values show modes still below 2019; negative values show modes above 2019. |
| System gap weight | Latest complete-year mode share multiplied by the positive baseline gap. Used to prioritise large modes that remain below baseline. |
| Priority band | Interpretation label derived from mode share and recovery level. |
| Next evidence needed | Suggested datasets required before moving from strategic monitoring to corridor, service, signal-priority or investment advice. |

## Dashboard Output Tables

| Output | Purpose |
|---|---|
| `annual_by_mode.csv` | Annual patronage by year and mode. |
| `annual_total.csv` | Annual total patronage across all modes. |
| `annual_totals_yoy.csv` | Annual total patronage with year-on-year change. |
| `mode_share.csv` | Annual mode share by year. |
| `latest_complete_year_mode_share.csv` | Mode share for the latest complete year. |
| `recovery_vs_2019.csv` | Mode-level recovery against the 2019 baseline. |
| `action_priority_matrix.csv` | Recovery gap, mode share, weighted system impact, priority band and suggested policy action. |
| `network_group_summary.csv` | Metropolitan versus Regional/VLine recovery and share summary. |
| `recommendation_matrix.csv` | Management recommendations linked to evidence and policy relevance. |

## Data Quality Notes

- One source value in the raw CSV included extra text after a numeric value: `940930Jan-25`.
- The Python cleaning function extracts the leading numeric value and preserves it as `940930`.
- 2026 is year-to-date only in the downloaded file, so complete-year comparisons use 2025.

## Known Limitations

- Monthly mode-level patronage does not identify station, route, corridor, time-of-day or service-level drivers.
- Patronage data alone does not establish causation.
- Policy interpretation should be combined with service frequency, reliability, fare policy, population growth, land-use change, major project delivery and stakeholder evidence.
