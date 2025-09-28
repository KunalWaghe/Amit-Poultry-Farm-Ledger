import sqlite3

# --- DATABASE SETUP SCRIPT ---
# This script should be run only ONCE to create and initialize the database.

# Connect to the database file (it will be created if it doesn't exist)
conn = sqlite3.connect('poultry.db')
cursor = conn.cursor()

print("Database connected. Setting up tables...")

# Drop tables if they exist to start fresh (useful for re-running the script)
cursor.execute("DROP TABLE IF EXISTS traders")
cursor.execute("DROP TABLE IF EXISTS transactions")
cursor.execute("DROP TABLE IF EXISTS daily_rates")

# Create the 'traders' table
cursor.execute("""
CREATE TABLE traders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    line TEXT NOT NULL,
    total_debt REAL NOT NULL DEFAULT 0.0
);
""")
print("Table 'traders' created.")

# Create the 'transactions' table
cursor.execute("""
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trader_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- 'Purchase' or 'Payment'
    date TEXT NOT NULL,
    details TEXT,
    total_amount REAL,
    amount_paid REAL,
    FOREIGN KEY (trader_id) REFERENCES traders (id)
);
""")
print("Table 'transactions' created.")

# Create the 'daily_rates' table
cursor.execute("""
CREATE TABLE daily_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    line TEXT NOT NULL,
    bird_type TEXT NOT NULL,
    rate REAL NOT NULL
);
""")
print("Table 'daily_rates' created.")


# --- INITIAL DATA INSERTION ---
# We'll insert the data we were using before into the new tables.

print("\nInserting initial data...")

# Insert initial traders
initial_traders = [
    (1, 'Rajesh Kumar', 'Pati', 5400.50),
    (2, 'Suresh Patel', 'Pati', 0.00),
    (3, 'Amit Singh', 'Anjad', 1230.00),
    (4, 'Deepak Jain', 'Dahi', 7800.00),
    (5, 'Local Customer 1', 'Local', 250.00)
]
cursor.executemany("INSERT INTO traders (id, name, line, total_debt) VALUES (?, ?, ?, ?)", initial_traders)
print(f"{len(initial_traders)} initial traders inserted.")


# Insert initial transactions
initial_transactions = [
    (1, 1, 'Purchase', '2025-09-27', 'Broiler: 50.0kg @ 110.0', 5500.50, 100.00),
    (2, 3, 'Purchase', '2025-09-26', 'Minar: 15 units @ 82.0', 1230.00, 0.00),
    (3, 1, 'Payment', '2025-09-28', 'Standalone Payment', 0, 2000.00)
]
cursor.executemany("INSERT INTO transactions (id, trader_id, type, date, details, total_amount, amount_paid) VALUES (?, ?, ?, ?, ?, ?, ?)", initial_transactions)
print(f"{len(initial_transactions)} initial transactions inserted.")


# Insert initial daily rates
initial_rates = [
    ('2025-09-28', 'Pati', 'Minar', 85.00),
    ('2025-09-28', 'Pati', 'Broiler', 112.50),
    ('2025-09-28', 'Pati', 'Parent', 105.00),
    ('2025-09-28', 'Anjad', 'Minar', 86.00),
    ('2025-09-28', 'Anjad', 'Broiler', 114.00),
    ('2025-09-27', 'Pati', 'Broiler', 110.00)
]
cursor.executemany("INSERT INTO daily_rates (date, line, bird_type, rate) VALUES (?, ?, ?, ?)", initial_rates)
print(f"{len(initial_rates)} initial rates inserted.")


# Commit the changes and close the connection
conn.commit()
conn.close()

print("\nDatabase setup complete and connection closed. You can now run the main app.py file.")
