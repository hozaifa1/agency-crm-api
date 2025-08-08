# In database.py

import sqlite3

def init_db(db_name: str):  # Accept the database name as an argument
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        sample_customers = [
            ('Hozaifa', '20hozaifa02@gmail.com', 'lead'),
            ('Fariha', 'fariha.fhf@gmail.com', 'active'),
            ('Hossain', 'hozaifah626@gmail.com', 'lead'),
        ]
        cursor.executemany(
            "INSERT INTO customers(name, email, status) VALUES(?, ?, ?)", sample_customers
        )
        print(f"Database '{db_name}' seeded with sample customers.")

    conn.commit()
    conn.close()