# Melbourne/Victoria Transport Activity Analysis

## Overview

This project analyses monthly public transport patronage by mode in Victoria using open DTP/DataVic data. It was built as a practical transport policy analytics portfolio to demonstrate a reproducible workflow:

Raw open data -> Python cleaning -> SQLite/SQL analysis -> dashboard-ready outputs -> policy-style findings.

The repository includes three connected case studies:

1. Patronage recovery against a 2019 baseline.
2. Mode-specific recovery and demand pressure.
3. Dashboard-ready evidence for stakeholder communication.

The upgraded analysis connects these case studies through an action-priority framework: recovery gap x mode share x next evidence needed. See `REPORT.md` for the full policy analytics report and `CASE_STUDIES.md` for the portfolio summary.

## Professional Deliverables

- `outputs/transport_policy_dashboard.html` - executive dashboard with KPI cards, trend, recovery analysis, mode share and evidence tables.
- `REPORT.md` - full policy analytics report with findings, action-priority matrix, recommendations, limitations and next evidence plan.
- `outputs/policy_brief.md` - one-page policy brief.
- `CASE_STUDIES.md` - three-part transport policy analytics portfolio summary.
- `METHODOLOGY.md` - reproducible workflow and rationale for Python, SQL and AI Agent support.
- `DATA_DICTIONARY.md` - field definitions, metric definitions and data quality notes.
- `STAKEHOLDER_BRIEFING.md` - executive message, interpretation and recommended next analysis.

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
DATA_DICTIONARY.md
METHODOLOGY.md
STAKEHOLDER_BRIEFING.md
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
    action_priority_matrix.csv
    annual_by_mode.csv
    annual_total.csv
    latest_12_months.csv
    mode_share.csv
    network_group_summary.csv
    recommendation_matrix.csv
    recovery_vs_2019.csv
  policy_brief.md
  transport_policy_dashboard.html
sql/
  analysis_queries.sql
src/
  analyse_transport_patronage.py
```

## How to Run

```bash
pip install -r requirements.txt
python3 src/analyse_transport_patronage.py
```

The script creates cleaned datasets, a SQLite database, dashboard-ready CSV files, SVG charts, an HTML dashboard, a policy brief and a full policy analytics report.

## Analysis Steps

1. Loaded raw monthly patronage data.
2. Standardised column names and converted year/month fields into a date column.
3. Cleaned a source-data quality issue where one regional bus value included extra text after the numeric count.
4. Reshaped the dataset from wide format into a long analytical table with one row per month and mode.
5. Loaded the cleaned data into SQLite.
6. Used SQL to calculate annual patronage, mode share, latest 12-month patronage and recovery against the 2019 baseline.
7. Built an action-priority matrix by connecting recovery gap with mode share.
8. Exported dashboard-ready tables, policy-style findings, recommendations and a full report.

## Key Findings

- Total 2025 public transport patronage was 490,207,817, or 81.3% of the 2019 pre-COVID baseline.
- Metropolitan modes carried 92.06% of 2025 patronage, but metropolitan train and tram remained below 80% of their 2019 baseline.
- Metropolitan Train is the highest diagnostic priority because it combines the largest 2025 mode share with the largest weighted recovery gap.
- V/Line Train showed the strongest recovery against 2019 at 119.36%, which is better treated as a growth and capacity monitoring question than a recovery-gap problem.

## Policy Relevance

This analysis could support DTP-style policy discussion by identifying where strategic recovery patterns should become operational investigation. The current project is strategic and mode-level; a next stage would combine patronage with land-use, service frequency, reliability, station/route-level, corridor-level, road traffic, intersection delay and signal-priority data.

## Limitations

- The dataset is monthly and mode-level, so it does not show route, station, corridor or time-of-day variation.
- 2026 is year-to-date only, so the analysis uses 2025 as the latest complete year.
- Patronage alone does not explain causation. It should be interpreted with service levels, network changes, population growth, land-use change, fare policy and stakeholder feedback.

## Interview Talking Point

I completed this project to refresh and demonstrate applied transport policy analytics. I used Python to clean and restructure open DTP/DataVic data, SQL to calculate repeatable trend and recovery metrics, and dashboard-ready outputs to communicate findings. The portfolio connects three case studies through an action-priority framework: recovery gap, mode share and next evidence needed. The main policy lesson is that data analysis should not stop at charts; it should translate evidence into a manager-ready work program, including limitations, operational data needs and practical recommendations.
