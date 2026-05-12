WITH jobs AS (

    SELECT *
    FROM {{ ref('stg_jobs') }}

)

SELECT

    job_id,
    title,
    employer_name,
    location,
    publication_date,
    occupation,

    description,

    CASE
        WHEN LOWER(description) LIKE '%python%'
        THEN 1 ELSE 0
    END AS python,

    CASE
        WHEN LOWER(description) LIKE '%sql%'
        THEN 1 ELSE 0
    END AS sql,

    CASE
        WHEN LOWER(description) LIKE '%dbt%'
        THEN 1 ELSE 0
    END AS dbt,

    CASE
        WHEN LOWER(description) LIKE '%duckdb%'
        THEN 1 ELSE 0
    END AS duckdb,

    CASE
        WHEN LOWER(description) LIKE '%spark%'
        THEN 1 ELSE 0
    END AS spark,

    CASE
        WHEN LOWER(description) LIKE '%tableau%'
        THEN 1 ELSE 0
    END AS tableau,

    CASE
        WHEN LOWER(description) LIKE '%power bi%'
        THEN 1 ELSE 0
    END AS power_bi,

    CASE
        WHEN LOWER(description) LIKE '%aws%'
        THEN 1 ELSE 0
    END AS aws,

    CASE
        WHEN LOWER(description) LIKE '%azure%'
        THEN 1 ELSE 0
    END AS azure,

    CASE
        WHEN LOWER(description) LIKE '%gcp%'
        THEN 1 ELSE 0
    END AS gcp,

    CASE
        WHEN LOWER(description) LIKE '%machine learning%'
        THEN 1 ELSE 0
    END AS machine_learning,

    CASE
        WHEN LOWER(description) LIKE '%pandas%'
        THEN 1 ELSE 0
    END AS pandas,

    CASE
        WHEN LOWER(description) LIKE '%numpy%'
        THEN 1 ELSE 0
    END AS numpy

FROM jobs