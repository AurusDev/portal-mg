import sqlite3
import os

# Database file is expected to be in the same directory based on my previous fix
db_file = os.path.abspath("portal_mg.db")
print(f"Connecting to database at: {db_file}")

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    email = "arthur.monteiro@mendoncagalvao.com.br"
    
    # Check current role
    cursor.execute("SELECT role FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row:
        print(f"Current role for {email}: {row[0]}")
        
        # Update role
        cursor.execute("UPDATE users SET role = 'admin' WHERE email = ?", (email,))
        conn.commit()
        print(f"Successfully updated role to 'admin' for {email}.")
        
        # Verify
        cursor.execute("SELECT role FROM users WHERE email = ?", (email,))
        new_row = cursor.fetchone()
        print(f"New role for {email}: {new_row[0]}")
    else:
        print(f"User {email} not found in database.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
