import duckdb

con = duckdb.connect("data/duckdb/job_market.duckdb")

query = """
SELECT
    search_term,
    COUNT(*) as total_jobs
FROM raw_jobs
GROUP BY search_term
ORDER BY total_jobs DESC
"""

df = con.execute(query).fetchdf()

print(df)
con.close()

