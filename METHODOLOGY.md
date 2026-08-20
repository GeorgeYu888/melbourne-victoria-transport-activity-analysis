# Methodology

## Objective

Build a reproducible transport policy analytics workflow that turns open DTP/DataVic patronage data into stakeholder-ready evidence.

## Analytical Workflow

1. Source raw monthly public transport patronage data.
2. Inspect column names, row count, date coverage and data types.
3. Clean column names into a consistent machine-readable format.
4. Convert `year` and `month` into a monthly date field.
5. Clean numeric fields and handle source-data quality issues.
6. Reshape the data from wide mode columns into a long analytical table.
7. Load the long table into SQLite.
8. Use SQL to calculate:
   - annual patronage by mode
   - total annual patronage
   - mode share
   - latest 12 months
   - recovery against 2019 baseline
   - year-on-year change
9. Export dashboard-ready CSV files.
10. Generate charts, an HTML dashboard and a policy brief.

## Why Python

Python is used for repeatable data cleaning and transformation. The project uses Python/pandas to standardise column names, convert dates, clean numeric values, reshape the table and regenerate all outputs from source.

## Why SQL

SQL is used for transparent analytical calculations. The queries are readable, reviewable and repeatable, which is important for policy analysis where findings may need to be checked by another analyst or manager.

## Why AI Agent Support

AI Agent support is used for workflow design, code assistance, logic checking and communication drafting. The evidence trail remains in the Python script, SQL queries, source data and exported outputs.

## Reproducibility

The project can be rerun with:

```bash
pip install -r requirements.txt
python src/analyse_transport_patronage.py
```

This regenerates the cleaned datasets, SQLite database, dashboard data, charts, HTML dashboard and policy brief.

## Policy Interpretation Approach

The analysis separates:

- What the data shows.
- What the data does not show.
- What policy questions should be investigated next.

This avoids overclaiming from mode-level monthly data and keeps recommendations suitable for a public-sector policy context.

