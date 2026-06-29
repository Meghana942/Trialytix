import sqlite3

def init_db():
    conn = sqlite3.connect("trialytix.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drug_name TEXT,
        disease TEXT,
        phase TEXT,
        enrollment INTEGER,
        start_year INTEGER,
        base_prob REAL,
        adjusted_prob REAL,
        risk_level TEXT,
        complexity REAL,
        benchmark REAL,
        recommendation TEXT
    )
    """)

    conn.commit()
    conn.close()