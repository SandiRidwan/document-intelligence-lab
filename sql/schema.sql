-- schema.sql — Skema DuckDB.
-- Lapisan: staging (hasil ekstraksi PDF) → marts (analitik).

-- ===========================================================================
-- STAGING
-- ===========================================================================

-- Sel tabel yang diekstrak dari PDF (dari parse.py)
CREATE TABLE IF NOT EXISTS stg_table_cells (
    source      VARCHAR,
    page        INTEGER,
    table_idx   INTEGER,
    row_idx     INTEGER,
    col_idx     INTEGER,
    col_name    VARCHAR,
    cell_raw    VARCHAR,
    cell_num    DOUBLE,
    is_numeric  BOOLEAN
);

-- Laporan kualitas per tabel/halaman (audit ekstraksi)
CREATE TABLE IF NOT EXISTS stg_parse_report (
    source             VARCHAR,
    page               INTEGER,
    table_idx          INTEGER,
    is_quality         BOOLEAN,
    n_rows             INTEGER,
    n_cols             INTEGER,
    numeric_ratio      DOUBLE,
    has_header         BOOLEAN,
    page_total_tables  INTEGER,
    page_quality_tables INTEGER
);

-- Indikator (label-angka) dari teks laporan (parse_extract.py)
CREATE TABLE IF NOT EXISTS stg_indicators (
    source     VARCHAR,
    page       INTEGER,
    region     VARCHAR,
    topic      VARCHAR,
    label      VARCHAR,
    value_raw  VARCHAR,
    value      DOUBLE,
    unit       VARCHAR
);

-- ===========================================================================
-- MARTS
-- ===========================================================================

-- Ringkasan ekstraksi per sumber (berapa banyak, berapa yang berkualitas)
CREATE TABLE IF NOT EXISTS mart_extraction_summary (
    source            VARCHAR PRIMARY KEY,
    pages_with_table  INTEGER,
    tables_detected   INTEGER,
    tables_quality    INTEGER,
    cells_extracted   INTEGER,
    indicators        INTEGER,
    quality_rate      DOUBLE
);

-- Indikator SDG per topik (agregat)
CREATE TABLE IF NOT EXISTS mart_indicators_by_topic (
    topic       VARCHAR,
    n_indicators INTEGER,
    n_pct       INTEGER,     -- berapa yang berupa persen
    n_regions   INTEGER      -- berapa yang punya label wilayah
);

-- Indikator per wilayah (untuk peta/penelusuran)
CREATE TABLE IF NOT EXISTS mart_indicators_by_region (
    region       VARCHAR,
    topic        VARCHAR,
    n_indicators INTEGER,
    avg_value    DOUBLE
);
