CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. Clean and enrich job postings
CREATE OR REPLACE TABLE analytics.dim_jobs AS
SELECT
    id AS job_id,
    TRIM(title) AS job_title,
    TRIM(company_name) AS company_name,
    COALESCE(NULLIF(TRIM(candidate_required_location), ''), 'Worldwide') AS location,
    job_type,
    CAST(publication_date AS TIMESTAMP) AS published_at,
    DATE_TRUNC('day', CAST(publication_date AS TIMESTAMP)) AS published_date,
    CASE
        WHEN LOWER(title) ~ '(intern|internship|graduate|junior|jr\.|entry)' THEN 'Entry / Junior'
        WHEN LOWER(title) ~ '(senior|sr\.|lead|principal|staff|head|manager)' THEN 'Senior / Lead'
        ELSE 'Mid-Level'
    END AS seniority_level,
    COALESCE(description, '') AS description_html,
    url AS job_url
FROM raw_jobs.data_jobs
WHERE id IS NOT NULL;

-- 2. Unpivot skill demand across all job descriptions
CREATE OR REPLACE TABLE analytics.fact_skill_demand AS
WITH skill_patterns AS (
    SELECT 'SQL' AS skill, '\bsql\b' AS pattern UNION ALL
    SELECT 'Python', '\bpython\b' UNION ALL
    SELECT 'Power BI', 'power\s?bi' UNION ALL
    SELECT 'Tableau', '\btableau\b' UNION ALL
    SELECT 'Excel', '\bexcel\b' UNION ALL
    SELECT 'dbt', '\bdbt\b' UNION ALL
    SELECT 'Snowflake', '\bsnowflake\b' UNION ALL
    SELECT 'BigQuery', 'big\s?query' UNION ALL
    SELECT 'Spark', '\bspark\b' UNION ALL
    SELECT 'AWS / Cloud', '\b(aws|azure|gcp)\b' UNION ALL
    SELECT 'R', '\br\b' UNION ALL
    SELECT 'Airflow', '\bairflow\b'
)
SELECT
    j.job_id,
    j.published_date,
    j.seniority_level,
    j.company_name,
    s.skill
FROM analytics.dim_jobs j
JOIN skill_patterns s
    ON regexp_matches(LOWER(j.description_html), s.pattern);
