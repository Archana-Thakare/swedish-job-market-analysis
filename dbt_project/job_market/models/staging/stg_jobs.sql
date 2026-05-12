WITH source AS (

    SELECT *
    FROM raw_jobs

),

cleaned AS (

    SELECT

        id AS job_id,

        LOWER(TRIM(headline)) AS title,

        description,

        LOWER(TRIM(employer_name)) AS employer_name,

        LOWER(TRIM(location)) AS location,

        CAST(publication_date AS TIMESTAMP) AS publication_date,

        LOWER(TRIM(occupation)) AS occupation,

        LOWER(TRIM(search_term)) AS search_term,

        webpage_url,

        source_type

    FROM source

),

deduplicated AS (

    SELECT *
    FROM cleaned
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY job_id
        ORDER BY publication_date DESC
    ) = 1

)

SELECT *
FROM deduplicated