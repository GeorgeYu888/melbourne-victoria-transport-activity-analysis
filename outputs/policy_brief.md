# Melbourne/Victoria Transport Activity Analysis

## Purpose

This project analyses DTP/DataVic monthly public transport patronage by mode to identify demand patterns, recovery against a 2019 baseline and dashboard-ready evidence for policy discussion.

## Data

- Source: Monthly public transport patronage by mode, DTP/DataVic.
- Coverage in downloaded file: January 2018 to June 2026.
- Modes: Metropolitan train, metropolitan tram, metropolitan bus, V/Line train, V/Line coach and regional bus.

## Method

1. Used Python/pandas to clean column names, convert date fields and reshape the data from wide mode columns into a long analytical table.
2. Loaded the cleaned table into SQLite so the analysis can be repeated with transparent SQL queries.
3. Produced dashboard-ready CSV outputs for annual patronage, mode share, latest 12 months and recovery against 2019.
4. Generated simple chart outputs and a policy-style brief focused on findings, limitations and next steps.

## Key Findings And Interpretation

1. Total patronage in 2025 was 490,207,817, equivalent to 81.3% of the 2019 pre-COVID baseline of 603,083,274.
2. The strongest recovery against 2019 was V/Line Train at 119.36% of baseline.
3. The weakest recovery against 2019 was Metropolitan Train at 75.66% of baseline.
4. The highest action-priority mode is Metropolitan Train, because it combines large 2025 mode share with a material recovery gap against 2019.

## Policy Relevance

The analysis helps identify which public transport modes have recovered more strongly and which may need closer investigation. The key policy point is not only whether a mode is above or below baseline; it is whether the mode is large enough to affect the system and whether its recovery pattern points to a concrete next evidence step.

## Recommended Action

Use the action-priority matrix to separate monitoring questions from investigation questions. For metropolitan rail, tram and bus, the next useful evidence would include corridor, station or route-level patronage, peak/off-peak demand, reliability, service frequency, traffic flow, signal delay and land-use context. For V/Line and regional services, the next useful evidence would include capacity, reliability and regional access monitoring.

## Limitations

- Monthly patronage is useful for strategic trends but does not show station, route, time-of-day or corridor-level variation.
- The file includes 2026 year-to-date data only, so complete-year comparisons use the latest complete year.
- Patronage patterns should be interpreted with land-use, service-level, population, fare policy and event context before making recommendations.

## Recommended Next Steps

1. Combine patronage trends with land-use and population growth data to understand demand drivers.
2. Compare mode-level trends with service frequency, reliability and major project delivery data.
3. Build a dashboard for non-technical stakeholders showing trend, recovery, mode share and limitations.
4. Extend the project with corridor or station-level datasets if available.
