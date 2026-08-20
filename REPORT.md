# Melbourne/Victoria Transport Policy Analytics Report

## Executive Summary

This report analyses open DTP/DataVic monthly public transport patronage by mode from January 2018 to June 2026. The purpose is not only to describe recovery, but to translate the evidence into a practical policy work program: which parts of the network deserve deeper diagnosis, what data should be added next, and what recommendations could be prepared for decision-makers.

The main finding is that Victorian public transport patronage has recovered substantially but unevenly. Total 2025 patronage was 490,207,817, equal to 81.3% of the 2019 baseline. The important policy connection is that metropolitan modes still carry 92.1% of 2025 patronage, but metropolitan train and tram remain below 80% of their 2019 baseline. That means the largest system impact is not simply where recovery is lowest; it is where weak recovery overlaps with a large share of total travel.

The action-priority matrix identifies Metropolitan Train as the highest diagnostic priority, followed by Metropolitan Tram. V/Line and regional services tell a different story: V/Line Train has recovered to 119.4% of 2019, and Regional/VLine services as a group have recovered to 108.0%. That should be treated as a growth and capacity monitoring question rather than the same type of recovery-gap problem.

## Policy Question

How has public transport activity in Melbourne and Victoria changed by mode, and what does the connection between recovery, mode share and operational evidence suggest for policy analysis, stakeholder advice and next-stage transport planning?

## Data Used

- Source: DTP/DataVic monthly public transport patronage by mode.
- Coverage in downloaded file: January 2018 to June 2026.
- Modes: Metropolitan Train, Metropolitan Tram, Metropolitan Bus, V/Line Train, V/Line Coach and Regional Bus.
- Analytical baseline: 2019 is used as the pre-COVID comparison year.
- Latest complete year: 2025. The file includes 2026 year-to-date records, but 2026 is not used as a complete-year comparison.

## How The Data Was Processed

Python was used to make the workflow repeatable and auditable. The script standardises column names, converts year and month into a monthly date field, cleans patronage values and reshapes the source from wide mode columns into a long analytical table with one row per month and mode.

One source-data quality issue was identified: a Regional Bus value contained text after the numeric count (`940930Jan-25`). The cleaning function extracts the leading numeric value and preserves it as a patronage count. This is recorded because public-sector analysis needs a visible evidence trail, not hidden cleaning assumptions.

SQLite was used to run repeatable SQL queries for annual patronage, mode share, latest 12-month records, recovery against 2019 and year-on-year change. The workflow exports dashboard-ready CSVs, chart files, an HTML dashboard and this report.

## Analytical Framework

The three case studies are connected by a single policy logic:

1. Recovery against 2019 shows whether activity has returned to the pre-COVID baseline.
2. Mode share shows whether a mode is large enough to materially affect the total system.
3. Action priority combines the two, so the analysis points to where a manager should ask for the next evidence pack.

This matters because a mode can have strong recovery but small total share, or weak recovery but large total share. Those situations require different policy responses.

## Findings

### The network has recovered, but the remaining gap is concentrated where the system is largest

Total 2025 patronage reached 490,207,817, or 81.3% of 2019. This is a strong recovery signal at the aggregate level, but it does not mean the network has returned uniformly to its pre-COVID pattern.

Metropolitan modes account for 92.1% of 2025 patronage. Because they carry most trips, weak recovery in metropolitan train and tram has a larger system-wide implication than a weak result in a smaller mode. This is the first connection across the case studies: recovery must be read together with mode share.

### Metropolitan Train is the highest diagnostic priority

Metropolitan Train has a 2025 mode share of 37.8% and a recovery rate of 75.7% against 2019. That combination creates the largest weighted recovery gap in the current dataset.

For a policy analyst, the next question is not simply "why is recovery low?" The useful question is more specific: which corridors, stations, time periods and user markets are driving the gap, and how much of the pattern is associated with service frequency, reliability, land-use change, office attendance, major projects, fare policy or other context?

### Metropolitan Tram requires a road-interface and land-use lens

Metropolitan Tram has a 2025 mode share of 31.4% and recovery of 77.4% against 2019. Because trams interact strongly with road conditions, intersection delay, inner-city land use, events and CBD travel patterns, mode-level patronage should be connected to route-level performance and traffic signal evidence before recommendations are made.

In a real DTP workflow, this would justify a follow-up pack that brings together route boardings, tram travel-time reliability, signal delay, road congestion, land-use activity and stakeholder feedback. That would support options such as targeted reliability work, signal-priority review or corridor-level service planning.

### Regional/VLine recovery is a different problem: growth, capacity and access

Regional/VLine services have recovered to 108.0% of 2019 as a group. V/Line Train is above its 2019 baseline at 119.4%. This should not be interpreted as "no problem"; it is a different type of policy question.

The next evidence need is capacity, reliability and access monitoring: are regional corridors experiencing growth pressure, are services reliable enough for current demand, and are timetable or infrastructure constraints emerging? This is where the analysis moves from recovery monitoring into forward planning.

## Action Priority Matrix

The matrix below ranks modes by a simple weighted recovery gap: 2025 mode share multiplied by the positive gap below 100% recovery. This is not a final investment model. It is a management tool for deciding where the next diagnostic effort should go.

| mode | mode_share_pct | recovery_pct | baseline_gap_pct | system_gap_weight | priority_band | suggested_policy_action |
| --- | --- | --- | --- | --- | --- | --- |
| Metropolitan Train | 37.78 | 75.66 | 24.34 | 919.57 | Highest diagnostic priority | Prepare a metro deep dive before recommending service or investment options |
| Metropolitan Tram | 31.35 | 77.38 | 22.62 | 709.14 | Highest diagnostic priority | Prepare a metro deep dive before recommending service or investment options |
| Metropolitan Bus | 22.93 | 90.89 | 9.11 | 208.89 | Monitor and investigate locally | Use route-level evidence to test targeted service reliability and priority interventions |
| Regional Bus | 2.41 | 89.74 | 10.26 | 24.73 | Monitor and investigate locally | Use route-level evidence to test targeted service reliability and priority interventions |
| V/Line Train | 5.25 | 119.36 | -19.36 | 0.00 | Growth and capacity monitoring | Monitor whether above-baseline demand is creating capacity, reliability or access pressure |
| V/Line Coach | 0.28 | 104.38 | -4.38 | 0.00 | Growth and capacity monitoring | Monitor whether above-baseline demand is creating capacity, reliability or access pressure |

## Recommendations

| decision_area | evidence_connection | recommendation | why_it_matters |
| --- | --- | --- | --- |
| Metropolitan rail and tram recovery | Metropolitan modes carry 92.1% of 2025 patronage, while metro train and tram remain below 80% of their 2019 baseline. | Commission a corridor/station/route diagnostic that separates peak/off-peak, weekday/weekend, reliability, service level and land-use effects. | A weak recovery in high-share modes has the largest system-wide patronage and revenue implications. |
| Regional/VLine growth pressure | Regional/VLine patronage has recovered to 108.0% of 2019, with V/Line Train and Coach above baseline. | Monitor corridor capacity, reliability and regional access outcomes so above-baseline demand is visible before it becomes an operational constraint. | Strong recovery in a smaller share of the network can still signal important growth pressure and equity/access questions. |
| Bus and road-interface opportunities | Metropolitan bus has a material share of 2025 patronage and sits between rail/tram weakness and V/Line strength. | Add route-level boardings, travel-time reliability, road congestion and intersection delay data to identify bus priority or signal-priority opportunities. | Bus improvements often depend on the road network, so patronage analysis should connect with traffic flow and signal performance evidence. |
| Executive reporting discipline | The current dataset supports monthly strategic monitoring but not causal or corridor-level conclusions. | Maintain a monthly dashboard, exception list and evidence log, and label each recommendation as monitor, investigate, trial or implement. | This keeps advice decision-ready while preventing overclaiming from mode-level patronage alone. |

## What This Means For Daily Policy Analyst Work

This project reflects the kind of evidence workflow a policy analyst would support in a transport department:

- Maintain a monthly dashboard that tracks recovery, mode share, exceptions and data-quality notes.
- Prepare short manager briefings that explain what changed, why it may matter and what evidence is still missing.
- Use SQL to make core metrics transparent and repeatable.
- Use Python to clean, reshape and regenerate outputs quickly when source data updates.
- Convert technical findings into stakeholder-ready recommendations, including clear caveats.
- Connect patronage evidence with operational datasets such as service reliability, route/station demand, traffic volumes, signal delay, corridor performance, land-use change and stakeholder feedback.

## Limitations And Next Evidence Needed

The current dataset is monthly and mode-level. It is strong enough for strategic monitoring, recovery comparison and prioritising further analysis. It is not enough to make final corridor, timetable, traffic-signal or investment recommendations.

The next stage should add:

- Station, stop, route or corridor-level patronage.
- Peak/off-peak and weekday/weekend splits.
- Service frequency, reliability and cancellation data.
- Road traffic volumes, travel-time reliability and intersection delay where bus or tram operations interact with road conditions.
- Signal-priority and corridor performance data for tram and bus reliability questions.
- Land-use, population, employment-centre and event context.
- Stakeholder feedback from operators, local government, passengers and planning teams.

## Conclusion

The key conclusion is that the system is not one recovery story. Metropolitan train and tram are large enough and weak enough against the 2019 baseline to justify deeper diagnostic work. Regional/VLine has recovered strongly enough to require growth and capacity monitoring. Bus analysis should connect patronage with road-network performance and signal-priority opportunities. A decision-ready transport policy workflow should therefore move from mode-level monitoring to corridor-level diagnosis, then to targeted options supported by operational and land-use evidence.
