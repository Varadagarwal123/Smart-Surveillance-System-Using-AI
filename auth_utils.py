import sqlite3
from streamlit_authenticator.utilities.hasher import Hasher

# ========== SQLite Auth Helper Functions ==========

def get_users_from_db():
    # Connect to the SQLite database (it will create the file if it doesn't exist)
    conn = sqlite3.connect("users.db")  # SQLite DB file
    cursor = conn.cursor()
    
    # Ensure the table exists (you can create it separately if needed)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        name TEXT,
                        password_hash TEXT)''')
    
    cursor.execute("SELECT username, name, password_hash FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return users

def format_credentials(users):
    credentials = {"usernames": {}}
    for user in users:
        credentials["usernames"][user[0]] = {
            "name": user[1],
            "password": user[2]
        }
    return credentials

def register_user(name, username, password):
    hashed_password = Hasher().hash(password)
    try:
        conn = sqlite3.connect("users.db")  # SQLite DB file
        cursor = conn.cursor()
        
        # Insert new user into the 'users' table
        cursor.execute("INSERT INTO users (username, name, password_hash) VALUES (?, ?, ?)",
                       (username, name, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # This indicates a duplicate username
