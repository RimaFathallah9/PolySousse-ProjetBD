import mysql.connector
from werkzeug.security import generate_password_hash
import sys
import os

# Add parent directory to path to import db config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DB_CONFIG

def migrate():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Connected to database.")

        # 1. Add deleted_at to members if not exists
        try:
            cursor.execute("SELECT deleted_at FROM members LIMIT 1")
        except mysql.connector.Error:
            print("Adding deleted_at column to members table...")
            cursor.execute("ALTER TABLE members ADD COLUMN deleted_at DATETIME DEFAULT NULL")
        
        # 2. Create users table
        print("Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'member') NOT NULL DEFAULT 'member',
                member_id INT,
                FOREIGN KEY (member_id) REFERENCES members(id_member) ON DELETE SET NULL
            )
        """)

        # 3. Seed Users
        users = [
            ('admin', 'admin123', 'admin'),
            ('member', 'member123', 'member')
        ]

        for username, password, role in users:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                print(f"Creating user: {username}")
                password_hash = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    (username, password_hash, role)
                )
            else:
                print(f"User {username} already exists.")

        conn.commit()
        print("Migration completed successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    migrate()
