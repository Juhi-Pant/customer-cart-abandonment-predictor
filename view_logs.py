import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("abandonment_logs.db")

# Run query and read into DataFrame
df = pd.read_sql("SELECT * FROM session_logs", conn)

# Show the result
print(df)
