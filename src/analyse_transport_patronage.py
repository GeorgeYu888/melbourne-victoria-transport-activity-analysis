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
    latest_year = int(annual_total["year"].max() - 1)
    latest_total = int(annual_total.loc[annual_total["year"] == latest_year, "total_patronage"].iloc[0])
    baseline_2019 = int(annual_total.loc[annual_total["year"] == 2019, "total_patronage"].iloc[0])
    recovery_total = latest_total / baseline_2019 * 100
    top_recovery = recovery.iloc[0]
    weakest_recovery = recovery.iloc[-1]
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

## Key Findings

1. Total patronage in {latest_year} was {latest_total:,}, equivalent to {recovery_total:.1f}% of the 2019 pre-COVID baseline of {baseline_2019:,}.
2. The strongest recovery against 2019 was {top_recovery['mode']} at {top_recovery['recovery_pct']}% of baseline.
3. The weakest recovery against 2019 was {weakest_recovery['mode']} at {weakest_recovery['recovery_pct']}% of baseline.

## Policy Relevance

The analysis helps identify which public transport modes have recovered more strongly and which may need closer investigation. For DTP-style policy work, this evidence could support questions about service planning, network demand, mode-specific pressures, stakeholder priorities and where more granular corridor, land-use or timetable analysis may be required.

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


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    wide, long_df = load_and_clean()
    write_database(long_df)
    results = run_queries()
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
    print(f"Analysis complete. Outputs written to: {PROJECT_DIR}")


if __name__ == "__main__":
    main()
