# Transport Policy Analytics Portfolio - Case Studies

This repository contains a three-part applied transport policy analytics portfolio using open DTP/DataVic public transport patronage data.

## Case Study 1: Patronage Recovery Against 2019 Baseline

### Policy question

How far has Victorian public transport patronage recovered compared with the 2019 pre-COVID baseline?

### Method

- Used Python/pandas to clean and reshape monthly patronage data.
- Used SQLite/SQL to calculate annual patronage by mode.
- Compared the latest complete year against 2019.
- Produced dashboard-ready CSV outputs and a policy-style brief.

### Key result

2025 total public transport patronage was 490,207,817, equivalent to 81.3% of the 2019 baseline.

### Policy relevance

This helps identify where recovery has been stronger or weaker and where further investigation may be needed before making service planning, network investment or stakeholder advice decisions.

## Case Study 2: Mode-Specific Recovery and Demand Pressure

### Policy question

Which transport modes recovered most strongly, and which modes may require closer policy attention?

### Method

- Used SQL to compare each mode's 2025 patronage with its 2019 baseline.
- Ranked modes by recovery percentage.
- Prepared dashboard-ready recovery data and chart output.

### Key result

- V/Line Train recovered above the 2019 baseline at 119.36%.
- V/Line Coach recovered above baseline at 104.38%.
- Metropolitan Train showed the weakest recovery at 75.66%.
- Metropolitan Tram recovered to 77.38%.

### Policy relevance

The recovery pattern suggests that patronage change is not uniform across the network. A policy analyst should avoid one-size-fits-all conclusions and should combine these findings with service frequency, reliability, land-use, station/route-level and stakeholder evidence.

## Case Study 3: Dashboard-Ready Evidence for Stakeholders

### Policy question

How can raw transport patronage data be converted into evidence that non-technical stakeholders can use?

### Method

- Cleaned raw source data into both wide and long formats.
- Created SQLite tables for repeatable SQL analysis.
- Exported dashboard-ready files:
  - annual patronage by mode
  - annual total patronage
  - mode share
  - latest 12 months
  - recovery against 2019
- Generated SVG charts for direct sharing.

### Key result

The project produces a reusable evidence workflow rather than a one-off chart. A stakeholder can review the README, SQL queries, Python script, dashboard CSV outputs and policy brief to understand how findings were produced.

### Policy relevance

This mirrors public-sector policy analysis practice: define the question, clean the evidence, make calculations repeatable, communicate limitations and translate findings into next steps.

## Interview Summary

I completed this project to demonstrate that I can apply Python, SQL, AI Agent support and dashboard-ready reporting to a transport policy question. The project includes three connected case studies: patronage recovery against a 2019 baseline, mode-specific recovery and dashboard-ready stakeholder evidence. My focus was not just coding; it was building an evidence trail that could support policy discussion, limitations and next steps.

