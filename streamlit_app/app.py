from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Swedish Job Market Analysis",
    layout="wide"
)

st.title("🇸🇪 Swedish Data Job Market Dashboard")

st.markdown("""
Analyze which tools and skills Swedish companies are hiring for right now.
""")

# ---------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = BASE_DIR / "data" / "duckdb" / "job_market.duckdb"

con = duckdb.connect(str(DB_PATH))

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

st.sidebar.header("Filters")

roles_query = """
SELECT DISTINCT occupation
FROM stg_jobs
WHERE occupation IS NOT NULL
ORDER BY occupation
"""

locations_query = """
SELECT DISTINCT location
FROM stg_jobs
WHERE location IS NOT NULL
ORDER BY location
"""

roles = con.execute(roles_query).fetchdf()["occupation"].tolist()
locations = con.execute(locations_query).fetchdf()["location"].tolist()

selected_role = st.sidebar.selectbox(
    "Select Role",
    ["All"] + roles
)

selected_location = st.sidebar.selectbox(
    "Select Location",
    ["All"] + locations
)

# ---------------------------------------------------
# DYNAMIC FILTER LOGIC
# ---------------------------------------------------

where_clauses = []

if selected_role != "All":
    where_clauses.append(
        f"occupation = '{selected_role}'"
    )

if selected_location != "All":
    where_clauses.append(
        f"location = '{selected_location}'"
    )

where_sql = ""

if where_clauses:
    where_sql = "WHERE " + " AND ".join(where_clauses)

# ---------------------------------------------------
# VIEW 1 — TOP SKILLS
# ---------------------------------------------------

st.header("📊 Top 20 Most In-Demand Skills")

skills_query = f"""
WITH filtered_jobs AS (

    SELECT *
    FROM mart_skill_demand
    {where_sql}

)

SELECT 'Python' AS skill, SUM(python) AS total_jobs FROM filtered_jobs
UNION ALL
SELECT 'SQL', SUM(sql) FROM filtered_jobs
UNION ALL
SELECT 'dbt', SUM(dbt) FROM filtered_jobs
UNION ALL
SELECT 'DuckDB', SUM(duckdb) FROM filtered_jobs
UNION ALL
SELECT 'Spark', SUM(spark) FROM filtered_jobs
UNION ALL
SELECT 'Tableau', SUM(tableau) FROM filtered_jobs
UNION ALL
SELECT 'Power BI', SUM(power_bi) FROM filtered_jobs
UNION ALL
SELECT 'AWS', SUM(aws) FROM filtered_jobs
UNION ALL
SELECT 'Azure', SUM(azure) FROM filtered_jobs
UNION ALL
SELECT 'GCP', SUM(gcp) FROM filtered_jobs
UNION ALL
SELECT 'Machine Learning', SUM(machine_learning) FROM filtered_jobs
UNION ALL
SELECT 'Pandas', SUM(pandas) FROM filtered_jobs
UNION ALL
SELECT 'NumPy', SUM(numpy) FROM filtered_jobs
ORDER BY total_jobs DESC
LIMIT 20
"""

skills_df = con.execute(skills_query).fetchdf()

fig_skills = px.bar(
    skills_df,
    x="skill",
    y="total_jobs",
    title="Most Requested Skills"
)

st.plotly_chart(fig_skills, use_container_width=True)

# ---------------------------------------------------
# VIEW 2 — JOBS BY CITY
# ---------------------------------------------------

st.header("📍 Jobs by City / Region")

cities_query = f"""
SELECT
    location,
    COUNT(*) AS total_jobs
FROM stg_jobs
{where_sql}
GROUP BY location
ORDER BY total_jobs DESC
LIMIT 20
"""

cities_df = con.execute(cities_query).fetchdf()

fig_cities = px.bar(
    cities_df,
    x="location",
    y="total_jobs",
    title="Data Job Openings by City"
)

st.plotly_chart(fig_cities, use_container_width=True)

# ---------------------------------------------------
# VIEW 3 — SKILL COMPARISON BY ROLE
# ---------------------------------------------------

st.header("🧠 Skill Comparison by Job Type")

comparison_query = """
SELECT

    CASE
        WHEN title LIKE '%scientist%' THEN 'Data Scientist'
        WHEN title LIKE '%analyst%' THEN 'Data Analyst'
        WHEN title LIKE '%engineer%' THEN 'Data Engineer'
        ELSE 'Other'
    END AS role_type,

    AVG(python) * 100 AS python,
    AVG(sql) * 100 AS sql,
    AVG(spark) * 100 AS spark,
    AVG(power_bi) * 100 AS power_bi,
    AVG(tableau) * 100 AS tableau,
    AVG(machine_learning) * 100 AS machine_learning

FROM mart_skill_demand
GROUP BY role_type
"""

comparison_df = con.execute(comparison_query).fetchdf()

comparison_melted = comparison_df.melt(
    id_vars="role_type",
    var_name="skill",
    value_name="percentage"
)

fig_compare = px.bar(
    comparison_melted,
    x="role_type",
    y="percentage",
    color="skill",
    barmode="group",
    title="Skill Demand by Role Type (%)"
)

st.plotly_chart(fig_compare, use_container_width=True)

# ---------------------------------------------------
# WORD CLOUD
# ---------------------------------------------------

st.header("☁️ Most Common Terms in Job Descriptions")

wordcloud_query = f"""
SELECT description
FROM stg_jobs
{where_sql}
"""

wordcloud_df = con.execute(wordcloud_query).fetchdf()

text = " ".join(
    wordcloud_df["description"]
    .dropna()
    .astype(str)
    .tolist()
)

wordcloud = WordCloud(
    width=1200,
    height=500,
    background_color="white"
).generate(text)

fig, ax = plt.subplots(figsize=(15, 6))

ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")

st.pyplot(fig)

# ---------------------------------------------------
# BONUS — RECENT POSTING TREND
# ---------------------------------------------------

st.header("📈 Job Posting Trend")

trend_query = """
SELECT
    DATE_TRUNC('month', publication_date) AS month,
    COUNT(*) AS total_postings
FROM stg_jobs
GROUP BY month
ORDER BY month
"""

trend_df = con.execute(trend_query).fetchdf()

fig_trend = px.line(
    trend_df,
    x="month",
    y="total_postings",
    markers=True,
    title="Job Posting Volume Over Time"
)

st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------------------------------
# CLOSE CONNECTION
# ---------------------------------------------------

con.close()