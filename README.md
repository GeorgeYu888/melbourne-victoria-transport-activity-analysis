# Melbourne/Victoria Transport Activity Analysis

## Overview

This project analyses monthly public transport patronage by mode in Victoria using open DTP/DataVic data. It was built as a practical transport policy analytics portfolio to demonstrate a reproducible workflow:

Raw open data -> Python cleaning -> SQLite/SQL analysis -> dashboard-ready outputs -> policy-style findings.

The repository includes three connected case studies:

1. Patronage recovery against a 2019 baseline.
2. Mode-specific recovery and demand pressure.
3. Dashboard-ready evidence for stakeholder communication.

See `CASE_STUDIES.md` for the detailed portfolio summary.

## Policy Question

How has Victorian public transport patronage changed by mode, and what does the recovery pattern suggest for transport planning, stakeholder discussion and further evidence gathering?

## Data Source

- Dataset: Monthly public transport patronage by mode
- Publisher: Department of Transport and Planning / DataVic
- Coverage in downloaded file: January 2018 to June 2026
- Modes: Metropolitan train, metropolitan tram, metropolitan bus, V/Line train, V/Line coach and regional bus

## Tools Used

- Python and pandas for cleaning, reshaping and preparing data
- SQLite and SQL for repeatable grouping, comparison, mode share and recovery analysis
- AI Agent support for workflow design, code checking and policy-brief drafting
- Dashboard-ready CSV outputs for charts, tables and stakeholder reporting

## Repository Structure

```text
CASE_STUDIES.md
data/
  raw/
    monthly_public_transport_patronage_by_mode.csv
  processed/
    patronage_clean_long.csv
    patronage_clean_wide.csv
    transport_patronage.sqlite
outputs/
  charts/
    annual_patronage_by_mode_2025.svg
    recovery_vs_2019_by_mode.svg
  dashboard_data/
    annual_by_mode.csv
    annual_total.csv
    latest_12_months.csv
    mode_share.csv
    recovery_vs_2019.csv
  policy_brief.md
sql/
  analysis_queries.sql
src/
  analyse_transport_patronage.py
```

## How to Run

```bash
pip install -r requirements.txt
python src/analyse_transport_patronage.py
```

The script creates cleaned datasets, a SQLite database, dashboard-ready CSV files, SVG charts and a policy brief.

## Analysis Steps

1. Loaded raw monthly patronage data.
2. Standardised column names and converted year/month fields into a date column.
3. Cleaned a source-data quality issue where one regional bus value included extra text after the numeric count.
4. Reshaped the dataset from wide format into a long analytical table with one row per month and mode.
5. Loaded the cleaned data into SQLite.
6. Used SQL to calculate annual patronage, mode share, latest 12-month patronage and recovery against the 2019 baseline.
7. Exported dashboard-ready tables and policy-style findings.

## Key Findings

- Total 2025 public transport patronage was 490,207,817.
- 2025 patronage was 81.3% of the 2019 pre-COVID baseline.
- V/Line Train showed the strongest recovery against 2019 at 119.36%.
- Metropolitan Train showed the weakest recovery against 2019 at 75.66%.

## Policy Relevance

This analysis could support DTP-style policy discussion by identifying which modes have recovered more strongly, which modes may require closer investigation and where further evidence could be added. The current project is strategic and mode-level; a next stage would combine patronage with land-use, service frequency, reliability, station/route-level and corridor-level data.

## Limitations

- The dataset is monthly and mode-level, so it does not show route, station, corridor or time-of-day variation.
- 2026 is year-to-date only, so the analysis uses 2025 as the latest complete year.
- Patronage alone does not explain causation. It should be interpreted with service levels, network changes, population growth, land-use change, fare policy and stakeholder feedback.

## Interview Talking Point

I completed this project to refresh and demonstrate applied transport policy analytics. I used Python to clean and restructure open DTP/DataVic data, SQL to calculate repeatable trend and recovery metrics, and dashboard-ready outputs to communicate findings. The portfolio includes three connected case studies: patronage recovery, mode-specific recovery and stakeholder-ready evidence outputs. The main policy lesson is that data analysis should not stop at charts; it should explain the evidence, limitations and next questions for decision-makers.
