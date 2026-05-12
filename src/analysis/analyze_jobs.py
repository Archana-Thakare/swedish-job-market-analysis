from pathlib import Path
import duckdb
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "data" / "duckdb" / "job_market.duckdb"

con = duckdb.connect(str(DB_PATH))

print("\n==============================")
print("SWEDISH JOB MARKET ANALYSIS")
print("==============================\n")

# ---------------------------------------------------
# 1. Most demanded skills
# ---------------------------------------------------

skills_query = """
SELECT *
FROM mart_skill_counts
ORDER BY total_jobs DESC
"""

skills_df = con.execute(skills_query).fetchdf()

print("\nTop Skills in Swedish Data Jobs")
print("--------------------------------")
print(skills_df)

# ---------------------------------------------------
# 2. Cities with most openings
# ---------------------------------------------------

cities_query = """
SELECT
    location,
    COUNT(*) AS total_jobs
FROM stg_jobs
GROUP BY location
ORDER BY total_jobs DESC
LIMIT 15
"""

cities_df = con.execute(cities_query).fetchdf()

print("\nTop Cities for Data Jobs")
print("--------------------------")
print(cities_df)

# ---------------------------------------------------
# 3. Most common job titles
# ---------------------------------------------------

titles_query = """
SELECT
    title,
    COUNT(*) AS total_jobs
FROM stg_jobs
GROUP BY title
ORDER BY total_jobs DESC
LIMIT 15
"""

titles_df = con.execute(titles_query).fetchdf()

print("\nMost Common Job Titles")
print("------------------------")
print(titles_df)

# ---------------------------------------------------
# 4. Skill demand by role type
# ---------------------------------------------------

roles_query = """
SELECT

    CASE
        WHEN title LIKE '%scientist%' THEN 'Data Scientist'
        WHEN title LIKE '%analyst%' THEN 'Data Analyst'
        WHEN title LIKE '%engineer%' THEN 'Data Engineer'
        ELSE 'Other'
    END AS role_type,

    AVG(python) * 100 AS python_pct,
    AVG(sql) * 100 AS sql_pct,
    AVG(spark) * 100 AS spark_pct,
    AVG(power_bi) * 100 AS power_bi_pct,
    AVG(tableau) * 100 AS tableau_pct,
    AVG(machine_learning) * 100 AS ml_pct

FROM mart_skill_demand
GROUP BY role_type
ORDER BY role_type
"""

roles_df = con.execute(roles_query).fetchdf()

print("\nSkill Demand by Role Type (%)")
print("--------------------------------")
print(roles_df)

# ---------------------------------------------------
# 5. Posting trends over time (Bonus)
# ---------------------------------------------------

trend_query = """
SELECT
    DATE_TRUNC('month', publication_date) AS month,
    COUNT(*) AS total_postings
FROM stg_jobs
WHERE publication_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY month
ORDER BY month
"""

trend_df = con.execute(trend_query).fetchdf()

print("\nJob Posting Trend (Last 3 Months)")
print("-----------------------------------")
print(trend_df)

con.close()

# Export results to CSV
DB_PATH = BASE_DIR / "data" / "processed" / "skill_counts.csv"
skills_df.to_csv(str(DB_PATH), index=False)

DB_PATH = BASE_DIR / "data" / "processed" / "city_counts.csv"
cities_df.to_csv(str(DB_PATH), index=False)

DB_PATH = BASE_DIR / "data" / "processed" / "job_titles.csv"
titles_df.to_csv(str(DB_PATH), index=False)

DB_PATH = BASE_DIR / "data" / "processed" / "role_skill_breakdown.csv"
roles_df.to_csv(str(DB_PATH), index=False)

DB_PATH = BASE_DIR / "data" / "processed" / "posting_trends.csv"
trend_df.to_csv(str(DB_PATH), index=False)