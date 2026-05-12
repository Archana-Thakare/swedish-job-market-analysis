WITH skill_data AS (

    SELECT *
    FROM {{ ref('mart_skill_demand') }}

)

SELECT 'python' AS skill, SUM(python) AS total_jobs FROM skill_data
UNION ALL
SELECT 'sql', SUM(sql) FROM skill_data
UNION ALL
SELECT 'dbt', SUM(dbt) FROM skill_data
UNION ALL
SELECT 'duckdb', SUM(duckdb) FROM skill_data
UNION ALL
SELECT 'spark', SUM(spark) FROM skill_data
UNION ALL
SELECT 'tableau', SUM(tableau) FROM skill_data
UNION ALL
SELECT 'power_bi', SUM(power_bi) FROM skill_data
UNION ALL
SELECT 'aws', SUM(aws) FROM skill_data
UNION ALL
SELECT 'azure', SUM(azure) FROM skill_data
UNION ALL
SELECT 'gcp', SUM(gcp) FROM skill_data
UNION ALL
SELECT 'machine_learning', SUM(machine_learning) FROM skill_data
UNION ALL
SELECT 'pandas', SUM(pandas) FROM skill_data
UNION ALL
SELECT 'numpy', SUM(numpy) FROM skill_data
ORDER BY total_jobs DESC