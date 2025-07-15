import sqlite3

conn = sqlite3.connect("abandonment_logs.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS session_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    is_product_details_viewed INTEGER,
    no_items_added_incart INTEGER,
    session_activity_count INTEGER,
    no_of_product_clicks INTEGER,
    bounce_rate REAL,
    time_spent_on_site REAL,
    is_user_logged_in INTEGER,
    user_prior_abandonment_history INTEGER,
    prediction REAL,
    timestamp_logged TEXT
)
''')

conn.commit()
conn.close()
