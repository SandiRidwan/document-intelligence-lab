-- transform.sql — STAGING → MARTS (SQL murni).

-- 1. Ringkasan ekstraksi per sumber
DELETE FROM mart_extraction_summary;
INSERT INTO mart_extraction_summary
WITH rep AS (
    SELECT source,
           COUNT(DISTINCT CASE WHEN page_total_tables > 0 THEN page END)
               AS pages_with_table,
           SUM(CASE WHEN table_idx >= 0 THEN 1 ELSE 0 END) AS tables_detected,
           SUM(CASE WHEN is_quality THEN 1 ELSE 0 END)    AS tables_quality
    FROM stg_parse_report GROUP BY source
),
cel AS (
    SELECT source, COUNT(*) AS cells FROM stg_table_cells GROUP BY source
),
ind AS (
    SELECT source, COUNT(*) AS indicators FROM stg_indicators GROUP BY source
)
SELECT
    r.source,
    COALESCE(r.pages_with_table, 0),
    COALESCE(r.tables_detected, 0),
    COALESCE(r.tables_quality, 0),
    COALESCE(c.cells, 0),
    COALESCE(i.indicators, 0),
    ROUND(COALESCE(r.tables_quality, 0)::DOUBLE
          / NULLIF(r.tables_detected, 0), 3) AS quality_rate
FROM rep r
LEFT JOIN cel c ON r.source = c.source
LEFT JOIN ind i ON r.source = i.source;

-- 2. Indikator per topik
DELETE FROM mart_indicators_by_topic;
INSERT INTO mart_indicators_by_topic
SELECT
    COALESCE(topic, '(tak ada topik)') AS topic,
    COUNT(*) AS n_indicators,
    SUM(CASE WHEN unit = '%' THEN 1 ELSE 0 END) AS n_pct,
    COUNT(DISTINCT region) AS n_regions
FROM stg_indicators
GROUP BY 1
ORDER BY n_indicators DESC;

-- 3. Indikator per wilayah-topik
DELETE FROM mart_indicators_by_region;
INSERT INTO mart_indicators_by_region
SELECT
    COALESCE(region, '(global/none)') AS region,
    COALESCE(topic, '(tanpa topik)') AS topic,
    COUNT(*) AS n_indicators,
    ROUND(AVG(value), 4) AS avg_value
FROM stg_indicators
GROUP BY 1, 2
HAVING COUNT(*) >= 2;
