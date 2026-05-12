import duckdb

db_path = r"C:\archana\swedish-job-market-analysis\data\duckdb\job_market.duckdb"

con = duckdb.connect(db_path)

tables = con.execute("SHOW TABLES").fetchall()

print("Tables:")
print(tables)

con.close()