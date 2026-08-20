-- Melbourne/Victoria Transport Activity Analysis
-- Data source: DTP / DataVic monthly public transport patronage by mode.

-- 1. Annual patronage by mode.
SELECT
  year,
  mode,
  SUM(patronage) AS annual_patronage
FROM patronage_long
GROUP BY year, mode
ORDER BY year, annual_patronage DESC;

-- 2. Total annual patronage across all modes.
SELECT
  year,
  SUM(patronage) AS total_patronage
FROM patronage_long
GROUP BY year
ORDER BY year;

-- 3. Mode share by year.
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
ORDER BY annual_mode.year, mode_share_pct DESC;

-- 4. Latest 12 months by mode.
SELECT
  date,
  mode,
  patronage
FROM patronage_long
WHERE date >= (
  SELECT DATE(MAX(date), '-11 months')
  FROM patronage_long
)
ORDER BY date, mode;

-- 5. Recovery comparison: latest complete year versus 2019 baseline.
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
ORDER BY recovery_pct DESC;

-- 6. Action-priority matrix: recovery gap x latest complete-year mode share.
-- This query supports management triage: large modes below baseline should be
-- investigated before small modes with limited system impact.
WITH annual_mode AS (
  SELECT year, mode, SUM(patronage) AS annual_patronage
  FROM patronage_long
  GROUP BY year, mode
),
latest AS (
  SELECT mode, annual_patronage AS latest_year
  FROM annual_mode
  WHERE year = (SELECT MAX(year) - 1 FROM patronage_long)
),
baseline AS (
  SELECT mode, annual_patronage AS baseline_2019
  FROM annual_mode
  WHERE year = 2019
),
latest_total AS (
  SELECT SUM(latest_year) AS total_latest
  FROM latest
)
SELECT
  latest.mode,
  latest.latest_year,
  baseline.baseline_2019,
  ROUND(100.0 * latest.latest_year / latest_total.total_latest, 2) AS mode_share_pct,
  ROUND(100.0 * latest.latest_year / baseline.baseline_2019, 2) AS recovery_pct,
  ROUND(100.0 - (100.0 * latest.latest_year / baseline.baseline_2019), 2) AS baseline_gap_pct,
  ROUND(
    (100.0 * latest.latest_year / latest_total.total_latest)
    * MAX(0, 100.0 - (100.0 * latest.latest_year / baseline.baseline_2019)),
    2
  ) AS system_gap_weight
FROM latest
JOIN baseline ON latest.mode = baseline.mode
CROSS JOIN latest_total
ORDER BY system_gap_weight DESC, mode_share_pct DESC;

-- 7. Network group summary: metropolitan versus regional/VLine recovery.
WITH annual_mode AS (
  SELECT
    year,
    CASE
      WHEN mode LIKE 'Metropolitan%' THEN 'Metropolitan'
      ELSE 'Regional/VLine'
    END AS network_group,
    SUM(patronage) AS annual_patronage
  FROM patronage_long
  GROUP BY year, network_group
),
latest AS (
  SELECT network_group, annual_patronage AS latest_year
  FROM annual_mode
  WHERE year = (SELECT MAX(year) - 1 FROM patronage_long)
),
baseline AS (
  SELECT network_group, annual_patronage AS baseline_2019
  FROM annual_mode
  WHERE year = 2019
),
latest_total AS (
  SELECT SUM(latest_year) AS total_latest
  FROM latest
)
SELECT
  latest.network_group,
  latest.latest_year,
  baseline.baseline_2019,
  ROUND(100.0 * latest.latest_year / latest_total.total_latest, 2) AS network_share_pct,
  ROUND(100.0 * latest.latest_year / baseline.baseline_2019, 2) AS recovery_vs_2019_pct
FROM latest
JOIN baseline ON latest.network_group = baseline.network_group
CROSS JOIN latest_total
ORDER BY latest.latest_year DESC;
