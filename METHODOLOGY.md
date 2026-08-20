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
   - action-priority matrix
   - network group summary
   - recommendation matrix
9. Export dashboard-ready CSV files.
10. Generate charts, an HTML dashboard, a policy brief and a full policy analytics report.

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
python3 src/analyse_transport_patronage.py
```

This regenerates the cleaned datasets, SQLite database, dashboard data, charts, HTML dashboard, policy brief and full report.

## Action-Priority Framework

The analysis uses a simple decision-support framework:

1. Calculate recovery against the 2019 baseline.
2. Calculate the latest complete-year mode share.
3. Calculate the positive baseline gap for modes below 100% recovery.
4. Weight the gap by mode share to identify where below-baseline recovery has the largest system impact.
5. Assign a priority band and next evidence requirement.

This framework is not a final investment model. It is a management tool for deciding where the next diagnostic pack should focus.

## Policy Interpretation Approach

The analysis separates:

- What the data shows.
- What the data does not show.
- What policy questions should be investigated next.

This avoids overclaiming from mode-level monthly data and keeps recommendations suitable for a public-sector policy context.

## Next-Stage Data Design

The project deliberately identifies what data would be needed for a more operational DTP-style analysis:

- station, stop, route or corridor patronage
- peak/off-peak and weekday/weekend demand
- service frequency, reliability, cancellations and crowding
- traffic volumes and road travel-time reliability for bus and tram corridors
- intersection delay and signal-priority evidence
- land-use, population, employment and event context
- operator, local government and passenger/stakeholder feedback
