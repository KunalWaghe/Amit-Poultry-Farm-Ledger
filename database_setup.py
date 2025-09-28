import sqlite3

# This script is run only once to set up the database.
DATABASE_NAME = 'poultry.db'

# Connect to the database (it will be created if it doesn't exist)
conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

print("Database connected. Setting up tables...")

# Drop existing tables to start fresh (important for schema changes)
cursor.execute('DROP TABLE IF EXISTS traders')
cursor.execute('DROP TABLE IF EXISTS transactions')
cursor.execute('DROP TABLE IF EXISTS daily_rates')
print("Existing tables dropped.")

# Create the 'traders' table
cursor.execute('''
CREATE TABLE traders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    line TEXT NOT NULL,
    total_debt REAL NOT NULL DEFAULT 0.0
)
''')
print("Table 'traders' created successfully.")

# Create the 'transactions' table with the new 'driver_name' column
cursor.execute('''
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trader_id INTEGER,
    type TEXT NOT NULL, -- 'Purchase' or 'Payment'
    date TEXT NOT NULL,
    details TEXT,
    driver_name TEXT, -- This is the new column
    total_amount REAL,
    amount_paid REAL,
    FOREIGN KEY (trader_id) REFERENCES traders (id)
)
''')
print("Table 'transactions' created with 'driver_name' column.")

# Create the 'daily_rates' table
cursor.execute('''
CREATE TABLE daily_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    line TEXT NOT NULL,
    bird_type TEXT NOT NULL,
    rate REAL NOT NULL
)
''')
print("Table 'daily_rates' created successfully.")

# --- INITIAL DATA (for testing) ---
traders_data = [
    ('Rajesh Kumar', 'Pati', 5400.00),
    ('Amit Singh', 'Anjad', 0.00),
    ('Suresh Patel', 'Pati', 1250.50),
    ('Vikas Jain', 'Local', -200.00)
]
cursor.executemany('INSERT INTO traders (name, line, total_debt) VALUES (?, ?, ?)', traders_data)
print(f"{len(traders_data)} initial traders inserted.")

# --- IMPORTANT NOTE ---
# Since you have an existing database, you must run this script again.
# This will delete your current database and create a new one with the updated structure.
# PLEASE BACK UP YOUR 'poultry.db' FILE IF YOU HAVE IMPORTANT DATA IN IT.

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database setup complete and connection closed.")

