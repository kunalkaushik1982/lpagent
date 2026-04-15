import sqlite3
import pandas as pd
import os

db_path = 'lp_agent.db'

if not os.path.exists(db_path):
    print(f"Error: Database file '{db_path}' not found.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    
    # Check if users table exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if not cursor.fetchone():
        print("Table 'users' does not exist.")
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Available tables: {tables}")
    else:
        # Fetch users
        users = pd.read_sql_query("SELECT id, username, password_hash, current_role, target_role, experience_years FROM users", conn)
        if users.empty:
            print("No users found in the database.")
        else:
            print("\n--- Users in Database ---")
            print(users.to_string(index=False))
            print("-------------------------")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals():
        conn.close()
