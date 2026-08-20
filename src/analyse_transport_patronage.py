from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_DIR / "data" / "raw" / "monthly_public_transport_patronage_by_mode.csv"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
DASHBOARD_DIR = PROJECT_DIR / "outputs" / "dashboard_data"
CHART_DIR = PROJECT_DIR / "outputs" / "charts"
BRIEF_PATH = PROJECT_DIR / "outputs" / "policy_brief.md"
HTML_DASHBOARD_PATH = PROJECT_DIR / "outputs" / "transport_policy_dashboard.html"
REPORT_PATH = PROJECT_DIR / "REPORT.md"
DB_PATH = PROCESSED_DIR / "transport_patronage.sqlite"


MODE_COLUMNS = [
    "Metropolitan train",
    "Metropolitan tram ",
    "Metropolitan bus",
    "V/Line train",
    "V/Line coach",
    "Regional bus",
]


def clean_number(value: object) -> int:
    if pd.isna(value):
        return 0
    cleaned = str(value).replace(",", "").strip()
    match = re.match(r"^\d+", cleaned)
    return int(match.group(0)) if match else 0


def load_and_clean() -> tuple[pd.DataFrame, pd.DataFrame]:
    wide = pd.read_csv(RAW_PATH)
    wide.columns = [col.strip().lower().replace("/", "_").replace(" ", "_") for col in wide.columns]
    wide["date"] = pd.to_datetime(
        wide["year"].astype(str) + "-" + wide["month"].astype(str).str.zfill(2) + "-01"
    )

    mode_cols = [col.strip().lower().replace("/", "_").replace(" ", "_") for col in MODE_COLUMNS]
    for col in mode_cols:
        wide[col] = wide[col].apply(clean_number)

    long_df = wide.melt(
        id_vars=["date", "year", "month", "month_name"],
        value_vars=mode_cols,
        var_name="mode",
        value_name="patronage",
    )
    long_df["mode"] = (
        long_df["mode"]
        .str.replace("_", " ")
        .str.replace("v line", "V/Line")
        .str.title()
        .str.replace("V/Line", "V/Line")
    )
    long_df["network_group"] = long_df["mode"].apply(
        lambda mode: "Metropolitan" if mode.startswith("Metropolitan") else "Regional/VLine"
    )
    return wide, long_df


def write_database(long_df: pd.DataFrame) -> None:
    with sqlite3.connect(DB_PATH) as con:
        long_df.to_sql("patronage_long", con, if_exists="replace", index=False)


def query_df(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql_query(sql, con)


def run_queries() -> dict[str, pd.DataFrame]:
    queries = {
        "annual_by_mode": """
            SELECT year, mode, SUM(patronage) AS annual_patronage
            FROM patronage_long
            GROUP BY year, mode
            ORDER BY year, annual_patronage DESC
        """,
        "annual_total": """
            SELECT year, SUM(patronage) AS total_patronage
            FROM patronage_long
            GROUP BY year
            ORDER BY year
        """,
        "mode_share": """
            WITH annual_mode AS (
              SELECT year, mode, SUM(patronage) AS annual_patronage
              FROM patronage_long
              GROUP BY year, mode
            ),
            annual_total AS (
              SELECT year, SUM(annual_patronage) AS total_patronage
              FROM annual_mode
              GROUP BY year
            )
            SELECT
              annual_mode.year,
              annual_mode.mode,
              annual_mode.annual_patronage,
              ROUND(100.0 * annual_mode.annual_patronage / annual_total.total_patronage, 2) AS mode_share_pct
            FROM annual_mode
            JOIN annual_total ON annual_mode.year = annual_total.year
            ORDER BY annual_mode.year, mode_share_pct DESC
        """,
        "latest_12_months": """
            SELECT date, mode, patronage
            FROM patronage_long
            WHERE date >= (
              SELECT DATE(MAX(date), '-11 months')
              FROM patronage_long
            )
            ORDER BY date, mode
        """,
        "recovery_vs_2019": """
            WITH baseline AS (
              SELECT mode, SUM(patronage) AS baseline_2019
              FROM patronage_long
              WHERE year = 2019
              GROUP BY mode
            ),
            latest AS (
              SELECT mode, SUM(patronage) AS latest_year
              FROM patronage_long
              WHERE year = (SELECT MAX(year) - 1 FROM patronage_long)
              GROUP BY mode
            )
            SELECT
              latest.mode,
              baseline.baseline_2019,
              latest.latest_year,
              ROUND(100.0 * latest.latest_year / baseline.baseline_2019, 2) AS recovery_pct
            FROM latest
            JOIN baseline ON latest.mode = baseline.mode
            ORDER BY recovery_pct DESC
        """,
        "annual_totals_yoy": """
            WITH annual AS (
              SELECT year, SUM(patronage) AS total_patronage
              FROM patronage_long
              GROUP BY year
            )
            SELECT
              year,
              total_patronage,
              LAG(total_patronage) OVER (ORDER BY year) AS previous_year_patronage,
              ROUND(
                100.0 * (total_patronage - LAG(total_patronage) OVER (ORDER BY year))
                / LAG(total_patronage) OVER (ORDER BY year),
                2
              ) AS yoy_change_pct
            FROM annual
            ORDER BY year
        """,
        "latest_complete_year_mode_share": """
            WITH annual_mode AS (
              SELECT year, mode, SUM(patronage) AS annual_patronage
              FROM patronage_long
              WHERE year = (SELECT MAX(year) - 1 FROM patronage_long)
              GROUP BY year, mode
            ),
            total AS (
              SELECT SUM(annual_patronage) AS total_patronage
              FROM annual_mode
            )
            SELECT
              mode,
              annual_patronage,
              ROUND(100.0 * annual_patronage / total.total_patronage, 2) AS mode_share_pct
            FROM annual_mode, total
            ORDER BY annual_patronage DESC
        """,
    }
    return {name: query_df(sql) for name, sql in queries.items()}


def export_dashboard_data(results: dict[str, pd.DataFrame], wide: pd.DataFrame, long_df: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    wide.to_csv(PROCESSED_DIR / "patronage_clean_wide.csv", index=False)
    long_df.to_csv(PROCESSED_DIR / "patronage_clean_long.csv", index=False)
    for name, df in results.items():
        df.to_csv(DASHBOARD_DIR / f"{name}.csv", index=False)


def build_priority_matrix(results: dict[str, pd.DataFrame]) -> pd.DataFrame:
    latest_share = results["latest_complete_year_mode_share"]
    recovery = results["recovery_vs_2019"]
    matrix = latest_share.merge(recovery, on="mode")
    matrix["baseline_gap_pct"] = (100 - matrix["recovery_pct"]).round(2)
    matrix["system_gap_weight"] = (matrix["mode_share_pct"] * matrix["baseline_gap_pct"].clip(lower=0)).round(2)

    def classify(row: pd.Series) -> str:
        if row["mode_share_pct"] >= 25 and row["recovery_pct"] < 85:
            return "Highest diagnostic priority"
        if row["mode_share_pct"] >= 15 and row["recovery_pct"] < 90:
            return "High diagnostic priority"
        if row["recovery_pct"] >= 100:
            return "Growth and capacity monitoring"
        return "Monitor and investigate locally"

    def next_evidence(row: pd.Series) -> str:
        mode = str(row["mode"])
        if "Train" in mode and "Metropolitan" in mode:
            return "Station/corridor patronage, peak-period loads, reliability, service frequency, CBD and employment-centre travel demand"
        if "Tram" in mode:
            return "Route-level boardings, tram travel-time reliability, CBD/inner-city land-use context, signal delay and event patterns"
        if "Bus" in mode and "Metropolitan" in mode:
            return "Route boardings, transfer nodes, bus travel-time reliability, road congestion, bus priority and signal-priority candidates"
        if "V/Line" in mode:
            return "Corridor growth, load factors, reliability, timetable capacity, regional population and employment access"
        return "Route-level demand, service frequency, reliability and regional access context"

    def policy_action(row: pd.Series) -> str:
        mode = str(row["mode"])
        if row["priority_band"] == "Highest diagnostic priority":
            return "Prepare a metro deep dive before recommending service or investment options"
        if row["priority_band"] == "High diagnostic priority":
            return "Identify route/corridor drivers and separate peak, off-peak, weekday and weekend demand"
        if row["priority_band"] == "Growth and capacity monitoring":
            return "Monitor whether above-baseline demand is creating capacity, reliability or access pressure"
        if "Bus" in mode:
            return "Use route-level evidence to test targeted service reliability and priority interventions"
        return "Continue monitoring and add local evidence before making a policy recommendation"

    matrix["priority_band"] = matrix.apply(classify, axis=1)
    matrix["next_evidence_needed"] = matrix.apply(next_evidence, axis=1)
    matrix["suggested_policy_action"] = matrix.apply(policy_action, axis=1)
    return matrix[
        [
            "mode",
            "annual_patronage",
            "mode_share_pct",
            "baseline_2019",
            "latest_year",
            "recovery_pct",
            "baseline_gap_pct",
            "system_gap_weight",
            "priority_band",
            "next_evidence_needed",
            "suggested_policy_action",
        ]
    ].sort_values(["system_gap_weight", "mode_share_pct"], ascending=False)


def build_network_summary(results: dict[str, pd.DataFrame]) -> pd.DataFrame:
    annual_by_mode = results["annual_by_mode"].copy()
    annual_by_mode["network_group"] = annual_by_mode["mode"].apply(
        lambda mode: "Metropolitan" if mode.startswith("Metropolitan") else "Regional/VLine"
    )
    latest_year = int(results["annual_total"]["year"].max() - 1)
    baseline = annual_by_mode[annual_by_mode["year"] == 2019]
    latest = annual_by_mode[annual_by_mode["year"] == latest_year]
    baseline_summary = baseline.groupby("network_group", as_index=False)["annual_patronage"].sum()
    latest_summary = latest.groupby("network_group", as_index=False)["annual_patronage"].sum()
    summary = latest_summary.merge(baseline_summary, on="network_group", suffixes=("_latest", "_2019"))
    total_latest = summary["annual_patronage_latest"].sum()
    summary["mode_group_share_pct"] = (100 * summary["annual_patronage_latest"] / total_latest).round(2)
    summary["recovery_vs_2019_pct"] = (
        100 * summary["annual_patronage_latest"] / summary["annual_patronage_2019"]
    ).round(2)
    return summary.sort_values("annual_patronage_latest", ascending=False)


def build_recommendation_matrix(priority_matrix: pd.DataFrame, network_summary: pd.DataFrame) -> pd.DataFrame:
    metro_share = float(
        network_summary.loc[
            network_summary["network_group"] == "Metropolitan", "mode_group_share_pct"
        ].iloc[0]
    )
    regional_recovery = float(
        network_summary.loc[
            network_summary["network_group"] == "Regional/VLine", "recovery_vs_2019_pct"
        ].iloc[0]
    )
    return pd.DataFrame(
        [
            {
                "decision_area": "Metropolitan rail and tram recovery",
                "evidence_connection": f"Metropolitan modes carry {metro_share:.1f}% of 2025 patronage, while metro train and tram remain below 80% of their 2019 baseline.",
                "recommendation": "Commission a corridor/station/route diagnostic that separates peak/off-peak, weekday/weekend, reliability, service level and land-use effects.",
                "why_it_matters": "A weak recovery in high-share modes has the largest system-wide patronage and revenue implications.",
            },
            {
                "decision_area": "Regional/VLine growth pressure",
                "evidence_connection": f"Regional/VLine patronage has recovered to {regional_recovery:.1f}% of 2019, with V/Line Train and Coach above baseline.",
                "recommendation": "Monitor corridor capacity, reliability and regional access outcomes so above-baseline demand is visible before it becomes an operational constraint.",
                "why_it_matters": "Strong recovery in a smaller share of the network can still signal important growth pressure and equity/access questions.",
            },
            {
                "decision_area": "Bus and road-interface opportunities",
                "evidence_connection": "Metropolitan bus has a material share of 2025 patronage and sits between rail/tram weakness and V/Line strength.",
                "recommendation": "Add route-level boardings, travel-time reliability, road congestion and intersection delay data to identify bus priority or signal-priority opportunities.",
                "why_it_matters": "Bus improvements often depend on the road network, so patronage analysis should connect with traffic flow and signal performance evidence.",
            },
            {
                "decision_area": "Executive reporting discipline",
                "evidence_connection": "The current dataset supports monthly strategic monitoring but not causal or corridor-level conclusions.",
                "recommendation": "Maintain a monthly dashboard, exception list and evidence log, and label each recommendation as monitor, investigate, trial or implement.",
                "why_it_matters": "This keeps advice decision-ready while preventing overclaiming from mode-level patronage alone.",
            },
        ]
    )


def markdown_table(df: pd.DataFrame) -> str:
    table = df.copy()
    for col in table.columns:
        if pd.api.types.is_float_dtype(table[col]):
            table[col] = table[col].map(lambda value: f"{value:.2f}")
        else:
            table[col] = table[col].astype(str)

    headers = list(table.columns)
    rows = table.values.tolist()
    header_row = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_row, separator, *body])


def svg_bar_chart(df: pd.DataFrame, label_col: str, value_col: str, path: Path, title: str) -> None:
    rows = df[[label_col, value_col]].copy()
    rows[value_col] = pd.to_numeric(rows[value_col])
    max_value = max(rows[value_col].max(), 1)
    width = 920
    row_height = 34
    left = 210
    top = 58
    chart_width = 620
    height = top + row_height * len(rows) + 60
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="24" y="32" font-family="Arial" font-size="22" font-weight="700">{title}</text>',
    ]
    for idx, row in rows.reset_index(drop=True).iterrows():
        y = top + idx * row_height
        bar_width = int((row[value_col] / max_value) * chart_width)
        label = str(row[label_col])
        value = f"{int(row[value_col]):,}"
        parts.append(f'<text x="24" y="{y + 20}" font-family="Arial" font-size="15">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y + 5}" width="{bar_width}" height="20" fill="#1565c0"/>')
        parts.append(f'<text x="{left + bar_width + 8}" y="{y + 20}" font-family="Arial" font-size="14">{value}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_policy_brief(results: dict[str, pd.DataFrame], long_df: pd.DataFrame) -> None:
    annual_total = results["annual_total"]
    recovery = results["recovery_vs_2019"]
    priority_matrix = results["action_priority_matrix"]
    latest_year = int(annual_total["year"].max() - 1)
    latest_total = int(annual_total.loc[annual_total["year"] == latest_year, "total_patronage"].iloc[0])
    baseline_2019 = int(annual_total.loc[annual_total["year"] == 2019, "total_patronage"].iloc[0])
    recovery_total = latest_total / baseline_2019 * 100
    top_recovery = recovery.iloc[0]
    weakest_recovery = recovery.iloc[-1]
    top_priority = priority_matrix.iloc[0]
    latest_month = pd.to_datetime(long_df["date"]).max().strftime("%B %Y")

    BRIEF_PATH.write_text(
        f"""# Melbourne/Victoria Transport Activity Analysis

## Purpose

This project analyses DTP/DataVic monthly public transport patronage by mode to identify demand patterns, recovery against a 2019 baseline and dashboard-ready evidence for policy discussion.

## Data

- Source: Monthly public transport patronage by mode, DTP/DataVic.
- Coverage in downloaded file: January 2018 to {latest_month}.
- Modes: Metropolitan train, metropolitan tram, metropolitan bus, V/Line train, V/Line coach and regional bus.

## Method

1. Used Python/pandas to clean column names, convert date fields and reshape the data from wide mode columns into a long analytical table.
2. Loaded the cleaned table into SQLite so the analysis can be repeated with transparent SQL queries.
3. Produced dashboard-ready CSV outputs for annual patronage, mode share, latest 12 months and recovery against 2019.
4. Generated simple chart outputs and a policy-style brief focused on findings, limitations and next steps.

## Key Findings And Interpretation

1. Total patronage in {latest_year} was {latest_total:,}, equivalent to {recovery_total:.1f}% of the 2019 pre-COVID baseline of {baseline_2019:,}.
2. The strongest recovery against 2019 was {top_recovery['mode']} at {top_recovery['recovery_pct']}% of baseline.
3. The weakest recovery against 2019 was {weakest_recovery['mode']} at {weakest_recovery['recovery_pct']}% of baseline.
4. The highest action-priority mode is {top_priority['mode']}, because it combines large 2025 mode share with a material recovery gap against 2019.

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
""",
        encoding="utf-8",
    )


def write_policy_report(results: dict[str, pd.DataFrame], long_df: pd.DataFrame) -> None:
    annual_total = results["annual_total"]
    priority_matrix = results["action_priority_matrix"]
    network_summary = results["network_group_summary"]
    recommendations = results["recommendation_matrix"]
    latest_year = int(annual_total["year"].max() - 1)
    latest_total = int(annual_total.loc[annual_total["year"] == latest_year, "total_patronage"].iloc[0])
    baseline_2019 = int(annual_total.loc[annual_total["year"] == 2019, "total_patronage"].iloc[0])
    recovery_total = latest_total / baseline_2019 * 100
    latest_month = pd.to_datetime(long_df["date"]).max().strftime("%B %Y")
    metro = network_summary.loc[network_summary["network_group"] == "Metropolitan"].iloc[0]
    regional = network_summary.loc[network_summary["network_group"] == "Regional/VLine"].iloc[0]
    top_priority = priority_matrix.iloc[0]
    second_priority = priority_matrix.iloc[1]
    strongest = priority_matrix.sort_values("recovery_pct", ascending=False).iloc[0]
    weakest = priority_matrix.sort_values("recovery_pct", ascending=True).iloc[0]

    priority_md = markdown_table(priority_matrix[
        [
            "mode",
            "mode_share_pct",
            "recovery_pct",
            "baseline_gap_pct",
            "system_gap_weight",
            "priority_band",
            "suggested_policy_action",
        ]
    ])
    recommendation_md = markdown_table(recommendations)

    REPORT_PATH.write_text(
        f"""# Melbourne/Victoria Transport Policy Analytics Report

## Executive Summary

This report analyses open DTP/DataVic monthly public transport patronage by mode from January 2018 to {latest_month}. The purpose is not only to describe recovery, but to translate the evidence into a practical policy work program: which parts of the network deserve deeper diagnosis, what data should be added next, and what recommendations could be prepared for decision-makers.

The main finding is that Victorian public transport patronage has recovered substantially but unevenly. Total 2025 patronage was {latest_total:,}, equal to {recovery_total:.1f}% of the 2019 baseline. The important policy connection is that metropolitan modes still carry {metro['mode_group_share_pct']:.1f}% of 2025 patronage, but metropolitan train and tram remain below 80% of their 2019 baseline. That means the largest system impact is not simply where recovery is lowest; it is where weak recovery overlaps with a large share of total travel.

The action-priority matrix identifies {top_priority['mode']} as the highest diagnostic priority, followed by {second_priority['mode']}. V/Line and regional services tell a different story: {strongest['mode']} has recovered to {strongest['recovery_pct']:.1f}% of 2019, and Regional/VLine services as a group have recovered to {regional['recovery_vs_2019_pct']:.1f}%. That should be treated as a growth and capacity monitoring question rather than the same type of recovery-gap problem.

## Policy Question

How has public transport activity in Melbourne and Victoria changed by mode, and what does the connection between recovery, mode share and operational evidence suggest for policy analysis, stakeholder advice and next-stage transport planning?

## Data Used

- Source: DTP/DataVic monthly public transport patronage by mode.
- Coverage in downloaded file: January 2018 to {latest_month}.
- Modes: Metropolitan Train, Metropolitan Tram, Metropolitan Bus, V/Line Train, V/Line Coach and Regional Bus.
- Analytical baseline: 2019 is used as the pre-COVID comparison year.
- Latest complete year: {latest_year}. The file includes 2026 year-to-date records, but 2026 is not used as a complete-year comparison.

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

Total 2025 patronage reached {latest_total:,}, or {recovery_total:.1f}% of 2019. This is a strong recovery signal at the aggregate level, but it does not mean the network has returned uniformly to its pre-COVID pattern.

Metropolitan modes account for {metro['mode_group_share_pct']:.1f}% of 2025 patronage. Because they carry most trips, weak recovery in metropolitan train and tram has a larger system-wide implication than a weak result in a smaller mode. This is the first connection across the case studies: recovery must be read together with mode share.

### Metropolitan Train is the highest diagnostic priority

{top_priority['mode']} has a 2025 mode share of {top_priority['mode_share_pct']:.1f}% and a recovery rate of {top_priority['recovery_pct']:.1f}% against 2019. That combination creates the largest weighted recovery gap in the current dataset.

For a policy analyst, the next question is not simply "why is recovery low?" The useful question is more specific: which corridors, stations, time periods and user markets are driving the gap, and how much of the pattern is associated with service frequency, reliability, land-use change, office attendance, major projects, fare policy or other context?

### Metropolitan Tram requires a road-interface and land-use lens

{second_priority['mode']} has a 2025 mode share of {second_priority['mode_share_pct']:.1f}% and recovery of {second_priority['recovery_pct']:.1f}% against 2019. Because trams interact strongly with road conditions, intersection delay, inner-city land use, events and CBD travel patterns, mode-level patronage should be connected to route-level performance and traffic signal evidence before recommendations are made.

In a real DTP workflow, this would justify a follow-up pack that brings together route boardings, tram travel-time reliability, signal delay, road congestion, land-use activity and stakeholder feedback. That would support options such as targeted reliability work, signal-priority review or corridor-level service planning.

### Regional/VLine recovery is a different problem: growth, capacity and access

Regional/VLine services have recovered to {regional['recovery_vs_2019_pct']:.1f}% of 2019 as a group. {strongest['mode']} is above its 2019 baseline at {strongest['recovery_pct']:.1f}%. This should not be interpreted as "no problem"; it is a different type of policy question.

The next evidence need is capacity, reliability and access monitoring: are regional corridors experiencing growth pressure, are services reliable enough for current demand, and are timetable or infrastructure constraints emerging? This is where the analysis moves from recovery monitoring into forward planning.

## Action Priority Matrix

The matrix below ranks modes by a simple weighted recovery gap: 2025 mode share multiplied by the positive gap below 100% recovery. This is not a final investment model. It is a management tool for deciding where the next diagnostic effort should go.

{priority_md}

## Recommendations

{recommendation_md}

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
""",
        encoding="utf-8",
    )


def fmt_int(value: float | int) -> str:
    return f"{int(value):,}"


def fmt_pct(value: float | int) -> str:
    return f"{float(value):.1f}%"


def build_inline_bar_rows(df: pd.DataFrame, label: str, value: str, max_value: float, suffix: str = "") -> str:
    rows = []
    for _, row in df.iterrows():
        width = max(2, float(row[value]) / max_value * 100)
        shown_value = f"{float(row[value]):.2f}{suffix}" if suffix else fmt_int(row[value])
        rows.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{row[label]}</div>
              <div class="bar-track"><div class="bar-fill" style="width:{width:.1f}%"></div></div>
              <div class="bar-value">{shown_value}</div>
            </div>
            """
        )
    return "\n".join(rows)


def build_line_svg(annual_totals: pd.DataFrame) -> str:
    rows = annual_totals.copy()
    min_year = int(rows["year"].min())
    max_year = int(rows["year"].max())
    min_value = float(rows["total_patronage"].min())
    max_value = float(rows["total_patronage"].max())
    width, height = 900, 260
    left, right, top, bottom = 70, 30, 30, 50
    plot_w = width - left - right
    plot_h = height - top - bottom

    def x(year: int) -> float:
        return left + (year - min_year) / max(max_year - min_year, 1) * plot_w

    def y(value: float) -> float:
        return top + (max_value - value) / max(max_value - min_value, 1) * plot_h

    points = " ".join(f"{x(int(r.year)):.1f},{y(float(r.total_patronage)):.1f}" for r in rows.itertuples())
    circles = "\n".join(
        f'<circle cx="{x(int(r.year)):.1f}" cy="{y(float(r.total_patronage)):.1f}" r="4"><title>{int(r.year)}: {fmt_int(r.total_patronage)}</title></circle>'
        for r in rows.itertuples()
    )
    year_labels = "\n".join(
        f'<text x="{x(int(r.year)):.1f}" y="{height - 18}" text-anchor="middle">{int(r.year)}</text>'
        for r in rows.itertuples()
    )
    return f"""
    <svg class="line-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Annual patronage trend">
      <line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" class="axis"/>
      <line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" class="axis"/>
      <polyline points="{points}" class="trend-line"/>
      <g class="points">{circles}</g>
      <g class="x-labels">{year_labels}</g>
      <text x="14" y="28" class="axis-note">{fmt_int(max_value)}</text>
      <text x="14" y="{height-bottom}" class="axis-note">{fmt_int(min_value)}</text>
    </svg>
    """


def write_html_dashboard(results: dict[str, pd.DataFrame], long_df: pd.DataFrame) -> None:
    annual_total = results["annual_total"]
    annual_yoy = results["annual_totals_yoy"]
    latest_share = results["latest_complete_year_mode_share"]
    recovery = results["recovery_vs_2019"]
    priority_matrix = results["action_priority_matrix"]
    recommendation_matrix = results["recommendation_matrix"]
    latest_12 = results["latest_12_months"]
    latest_year = int(annual_total["year"].max() - 1)
    latest_total = int(annual_total.loc[annual_total["year"] == latest_year, "total_patronage"].iloc[0])
    baseline = int(annual_total.loc[annual_total["year"] == 2019, "total_patronage"].iloc[0])
    recovery_total = latest_total / baseline * 100
    latest_month = pd.to_datetime(long_df["date"]).max().strftime("%B %Y")
    top_mode = recovery.iloc[0]
    low_mode = recovery.iloc[-1]
    ytd_2026 = int(annual_total.loc[annual_total["year"] == 2026, "total_patronage"].iloc[0])

    recovery_rows = build_inline_bar_rows(recovery, "mode", "recovery_pct", recovery["recovery_pct"].max(), "%")
    share_rows = build_inline_bar_rows(latest_share, "mode", "mode_share_pct", latest_share["mode_share_pct"].max(), "%")
    line_svg = build_line_svg(annual_total)

    latest_table = latest_12.tail(18).to_html(index=False, classes="data-table", border=0)
    yoy_table = annual_yoy.to_html(index=False, classes="data-table", border=0)
    priority_table = priority_matrix[
        [
            "mode",
            "mode_share_pct",
            "recovery_pct",
            "system_gap_weight",
            "priority_band",
            "suggested_policy_action",
        ]
    ].to_html(index=False, classes="data-table", border=0)
    recommendation_table = recommendation_matrix.to_html(index=False, classes="data-table", border=0)

    HTML_DASHBOARD_PATH.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Melbourne/Victoria Transport Policy Analytics Dashboard</title>
  <style>
    :root {{
      --ink: #17202a;
      --muted: #5d6d7e;
      --line: #d7dde5;
      --panel: #f7f9fb;
      --blue: #1565c0;
      --green: #13795b;
      --amber: #9a6500;
      --bg: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.45;
    }}
    header {{
      padding: 32px 44px 18px;
      border-bottom: 1px solid var(--line);
      background: #fbfcfd;
    }}
    main {{ padding: 24px 44px 48px; max-width: 1240px; margin: 0 auto; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin: 28px 0 12px; font-size: 20px; }}
    h3 {{ margin: 0 0 8px; font-size: 15px; }}
    p {{ margin: 0 0 10px; }}
    .subtitle {{ max-width: 980px; color: var(--muted); font-size: 15px; }}
    .meta {{ margin-top: 12px; color: var(--muted); font-size: 13px; }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .kpi {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: #fff;
      min-height: 116px;
    }}
    .kpi .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
    .kpi .value {{ font-size: 25px; font-weight: 700; margin: 8px 0 5px; }}
    .kpi .note {{ color: var(--muted); font-size: 13px; }}
    .grid-2 {{
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(0, .9fr);
      gap: 16px;
      align-items: start;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      background: #fff;
      margin-bottom: 16px;
    }}
    .panel.tint {{ background: var(--panel); }}
    .finding-list {{ padding-left: 18px; margin: 8px 0 0; }}
    .finding-list li {{ margin: 8px 0; }}
    .bar-row {{
      display: grid;
      grid-template-columns: 160px minmax(180px, 1fr) 86px;
      gap: 10px;
      align-items: center;
      margin: 9px 0;
      font-size: 13px;
    }}
    .bar-track {{ height: 18px; background: #e9eef5; border-radius: 4px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: var(--blue); }}
    .bar-value {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .line-chart {{ width: 100%; height: auto; }}
    .axis {{ stroke: #9aa7b6; stroke-width: 1; }}
    .trend-line {{ fill: none; stroke: var(--blue); stroke-width: 3; }}
    .points circle {{ fill: var(--green); }}
    .x-labels text, .axis-note {{ font-size: 12px; fill: var(--muted); font-family: Arial, Helvetica, sans-serif; }}
    .data-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    .data-table th, .data-table td {{ border-bottom: 1px solid var(--line); padding: 7px 8px; text-align: left; }}
    .data-table th {{ background: var(--panel); }}
    .badge {{
      display: inline-block;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 9px;
      margin: 3px 4px 3px 0;
      font-size: 12px;
      background: #fff;
    }}
    footer {{
      border-top: 1px solid var(--line);
      padding: 18px 44px 34px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 900px) {{
      header, main, footer {{ padding-left: 18px; padding-right: 18px; }}
      .kpi-grid, .grid-2 {{ grid-template-columns: 1fr; }}
      .bar-row {{ grid-template-columns: 1fr; gap: 4px; }}
      .bar-value {{ text-align: left; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Melbourne/Victoria Transport Policy Analytics Dashboard</h1>
    <p class="subtitle">A source-backed dashboard using open DTP/DataVic monthly public transport patronage data. It converts raw mode-level data into repeatable SQL metrics, dashboard-ready evidence and policy-ready interpretation.</p>
    <p class="meta">Source coverage: January 2018 to {latest_month}. Latest complete year used for annual comparison: {latest_year}. Generated from Python + SQLite workflow.</p>
  </header>
  <main>
    <section class="kpi-grid" aria-label="Key metrics">
      <div class="kpi"><div class="label">2025 patronage</div><div class="value">{fmt_int(latest_total)}</div><div class="note">Total trips across six public transport modes.</div></div>
      <div class="kpi"><div class="label">Recovery vs 2019</div><div class="value">{fmt_pct(recovery_total)}</div><div class="note">2019 baseline: {fmt_int(baseline)}.</div></div>
      <div class="kpi"><div class="label">Strongest recovery</div><div class="value">{top_mode['mode']}</div><div class="note">{top_mode['recovery_pct']}% of 2019 baseline.</div></div>
      <div class="kpi"><div class="label">Weakest recovery</div><div class="value">{low_mode['mode']}</div><div class="note">{low_mode['recovery_pct']}% of 2019 baseline.</div></div>
    </section>

    <section class="grid-2">
      <div class="panel">
        <h2>Annual Patronage Trend</h2>
        {line_svg}
      </div>
      <div class="panel tint">
        <h2>Policy Reading</h2>
        <ul class="finding-list">
          <li>Public transport recovery is uneven across modes, so mode-specific diagnosis is more useful than a single network-wide conclusion.</li>
          <li>The most useful policy connection is recovery gap multiplied by system share: large modes below baseline deserve deeper diagnosis first.</li>
          <li>Road-interface evidence matters for bus and tram analysis: traffic flow, intersection delay and signal priority can change reliability and therefore patronage outcomes.</li>
        </ul>
      </div>
    </section>

    <section class="panel">
      <h2>Action Priority Matrix</h2>
      <p>The matrix combines 2025 mode share with recovery against the 2019 baseline. This avoids treating a small high-recovery mode and a large weak-recovery mode as equally important for system planning.</p>
      {priority_table}
    </section>

    <section class="panel">
      <h2>Recommendations For Further Analysis</h2>
      <p>These are not final operational decisions. They are the next evidence steps a policy analyst should prepare before advising on service, corridor, signal-priority or investment options.</p>
      {recommendation_table}
    </section>

    <section class="grid-2">
      <div class="panel">
        <h2>Recovery Against 2019 by Mode</h2>
        {recovery_rows}
      </div>
      <div class="panel">
        <h2>{latest_year} Mode Share</h2>
        {share_rows}
      </div>
    </section>

    <section class="panel">
      <h2>Analytical Workflow</h2>
      <span class="badge">Raw CSV</span>
      <span class="badge">Python cleaning</span>
      <span class="badge">Data quality check</span>
      <span class="badge">Wide-to-long reshape</span>
      <span class="badge">SQLite evidence base</span>
      <span class="badge">SQL metrics</span>
      <span class="badge">Dashboard-ready CSV</span>
      <span class="badge">Policy brief</span>
      <p class="meta">This workflow is designed for reproducibility: the dashboard numbers reconcile to exported SQL result tables and the source data remains visible in the repository.</p>
    </section>

    <section class="grid-2">
      <div class="panel">
        <h2>Annual Totals and YoY Change</h2>
        {yoy_table}
      </div>
      <div class="panel">
        <h2>Latest 12 Months Detail</h2>
        {latest_table}
      </div>
    </section>
  </main>
  <footer>
    Built by George Yu as an applied transport policy analytics portfolio. Data source: Department of Transport and Planning / DataVic monthly public transport patronage by mode.
  </footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    wide, long_df = load_and_clean()
    write_database(long_df)
    results = run_queries()
    results["action_priority_matrix"] = build_priority_matrix(results)
    results["network_group_summary"] = build_network_summary(results)
    results["recommendation_matrix"] = build_recommendation_matrix(
        results["action_priority_matrix"], results["network_group_summary"]
    )
    export_dashboard_data(results, wide, long_df)

    latest_year = int(results["annual_total"]["year"].max() - 1)
    latest_by_mode = results["annual_by_mode"]
    latest_by_mode = latest_by_mode[latest_by_mode["year"] == latest_year]
    svg_bar_chart(
        latest_by_mode,
        "mode",
        "annual_patronage",
        CHART_DIR / f"annual_patronage_by_mode_{latest_year}.svg",
        f"Annual Public Transport Patronage by Mode, {latest_year}",
    )
    svg_bar_chart(
        results["recovery_vs_2019"],
        "mode",
        "recovery_pct",
        CHART_DIR / "recovery_vs_2019_by_mode.svg",
        "Recovery Against 2019 Baseline by Mode (%)",
    )
    write_policy_brief(results, long_df)
    write_policy_report(results, long_df)
    write_html_dashboard(results, long_df)
    print(f"Analysis complete. Outputs written to: {PROJECT_DIR}")


if __name__ == "__main__":
    main()
