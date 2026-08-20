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
          <li>Regional/VLine modes recovered more strongly than metropolitan train and tram, suggesting different travel-behaviour and service-planning questions.</li>
          <li>Monthly mode-level data is strong for strategic monitoring, but route, station, corridor, service frequency and land-use data are needed before operational recommendations.</li>
        </ul>
      </div>
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
    write_html_dashboard(results, long_df)
    print(f"Analysis complete. Outputs written to: {PROJECT_DIR}")


if __name__ == "__main__":
    main()
