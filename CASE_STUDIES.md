# Transport Policy Analytics Portfolio - Case Studies

This repository contains a three-part applied transport policy analytics portfolio using open DTP/DataVic public transport patronage data.

The three case studies are designed to connect with each other. The analysis starts with a recovery question, adds mode share to understand system importance, and then turns the evidence into an action-priority matrix for further policy work.

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

### Connection to the wider analysis

This establishes the baseline gap, but it is not enough by itself. A smaller mode can recover strongly without changing the total system very much, while a large mode can remain below baseline and create a bigger planning issue. That is why the next case study adds mode-level demand pressure and system share.

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
- Metropolitan modes carried 92.06% of 2025 patronage, so metropolitan recovery patterns dominate the system-level question.

### Connection to the wider analysis

The recovery pattern suggests that patronage change is not uniform across the network. The policy issue is not simply "which mode recovered most?" The better question is "which recovery gaps matter most for the system, and what evidence should a manager request next?"

This is why the analysis creates an action-priority matrix. Metropolitan Train and Metropolitan Tram are the highest diagnostic priorities because they combine high mode share with below-baseline recovery. V/Line recovery is strong, so the next question is capacity, reliability and regional access monitoring rather than recovery-gap diagnosis.

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
- Built an action-priority matrix and recommendation matrix:
  - recovery gap
  - 2025 mode share
  - weighted system impact
  - next evidence needed
  - suggested policy action

### Key result

The project produces a reusable evidence workflow rather than a one-off chart. A stakeholder can review the README, SQL queries, Python script, dashboard CSV outputs, action-priority matrix, dashboard, policy brief and full report to understand how findings were produced and what should happen next.

### Policy relevance

This mirrors public-sector policy analysis practice: define the question, clean the evidence, make calculations repeatable, communicate limitations and translate findings into next steps. In a real DTP work setting, the next evidence pack would connect mode-level patronage with corridor, station, route, traffic flow, intersection delay, signal-priority, reliability and land-use data.

## Cross-Case Insight

The strongest insight comes from linking the three case studies:

- **Recovery alone can mislead.** A mode above 100% recovery may still represent a small share of the total system.
- **Mode share changes the priority.** Metropolitan Train and Tram are high priorities because their below-baseline recovery affects a large share of total patronage.
- **Operational data is the next step.** Current mode-level data should trigger corridor and route diagnostics, not final operational decisions.
- **Road-interface evidence matters.** Bus and tram recommendations need traffic flow, intersection delay, signal priority and travel-time reliability evidence, not patronage alone.

## Interview Summary

I completed this project to demonstrate that I can apply Python, SQL, AI Agent support and dashboard-ready reporting to a transport policy question. The project includes three connected case studies: patronage recovery against a 2019 baseline, mode-specific recovery and stakeholder-ready evidence. My focus was not just coding; it was building an evidence trail that could support policy discussion, limitations, action priorities and next-stage recommendations.
