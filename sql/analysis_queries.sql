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
