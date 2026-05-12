import requests
import pandas as pd
import duckdb
import json
import os
from datetime import datetime

BASE_URL = "https://jobsearch.api.jobtechdev.se/search"

SEARCH_TERMS = [
    "data scientist",
    "data analyst",
    "data engineer",
    "machine learning"
]

HEADERS = {
    "accept": "application/json"
}

MAX_RESULTS_PER_TERM = 200

all_jobs = []

for term in SEARCH_TERMS:
    print(f"Fetching jobs for: {term}")

    params = {
        "q": term,
        "limit": 100
    }

    total_fetched = 0
    offset = 0

    while total_fetched < MAX_RESULTS_PER_TERM:

        params["offset"] = offset

        response = requests.get(
            BASE_URL,
            headers=HEADERS,
            params=params
        )

        if response.status_code != 200:
            print(f"Error fetching {term}: {response.status_code}")
            break

        data = response.json()

        hits = data.get("hits", [])

        if not hits:
            break

        for job in hits:

            employer = None
            workplace = None
            occupation = None

            if job.get("employer"):
                employer = job["employer"].get("name")

            if job.get("workplace_address"):
                workplace = job["workplace_address"].get("municipality")

            if job.get("occupation"):
                occupation = job["occupation"].get("label")

            all_jobs.append({
                "id": job.get("id"),
                "search_term": term,
                "headline": job.get("headline"),
                "description": job.get("description", {}).get("text"),
                "employer_name": employer,
                "location": workplace,
                "publication_date": job.get("publication_date"),
                "occupation": occupation,
                "source_type": job.get("source_type"),
                "webpage_url": job.get("webpage_url")
            })

        fetched_count = len(hits)
        total_fetched += fetched_count
        offset += fetched_count

        print(f"Fetched {total_fetched} jobs for {term}")

print(f"\nTotal jobs collected: {len(all_jobs)}")

# Remove duplicates
df = pd.DataFrame(all_jobs)

df = df.drop_duplicates(subset=["id"])

print(f"Unique jobs after deduplication: {len(df)}")

# Create folders if they don't exist
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/duckdb", exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save JSON
json_path = f"data/raw/jobtech_jobs_{timestamp}.json"

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(
        df.to_dict(orient="records"),
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"Saved JSON to {json_path}")

# Save CSV
csv_path = f"data/raw/jobtech_jobs_{timestamp}.csv"

df.to_csv(csv_path, index=False)

print(f"Saved CSV to {csv_path}")

# Save to DuckDB
db_path = "data/duckdb/job_market.duckdb"

con = duckdb.connect(db_path)

con.execute("""
CREATE TABLE IF NOT EXISTS raw_jobs AS
SELECT * FROM df LIMIT 0
""")

con.execute("""
INSERT INTO raw_jobs
SELECT * FROM df
""")

print(f"Saved data to DuckDB: {db_path}")

# Quick verification query
result = con.execute("""
SELECT occupation, COUNT(*) as total_jobs
FROM raw_jobs
GROUP BY occupation
ORDER BY total_jobs DESC
LIMIT 10
""").fetchdf()

print("\nTop occupations:")
print(result)

con.close()