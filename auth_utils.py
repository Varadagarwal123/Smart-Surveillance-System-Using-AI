# auth_utils.py

import mysql.connector
from mysql.connector import Error
from streamlit_authenticator.utilities.hasher import Hasher

# ========== MySQL Auth Helper Functions ==========

def get_users_from_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="varad@14",
        database="violence_detection"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, name, password_hash FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def format_credentials(users):
    credentials = {"usernames": {}}
    for user in users:
        credentials["usernames"][user["username"]] = {
            "name": user["name"],
            "password": user["password_hash"]
        }
    return credentials

def register_user(name, username, password):
    hashed_password = Hasher().hash(password)
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="varad@14",
            database="violence_detection"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, name, password_hash) VALUES (%s, %s, %s)",
                       (username, name, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        return False
