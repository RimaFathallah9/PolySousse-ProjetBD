import mysql.connector
import os

#Configuration
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
}

def init_db():
    print("Connecting to MySQL server...")
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        
        # Read and execute schema.sql
        print("Reading schema.sql...")
        with open('database/schema.sql', 'r') as f:
            schema_sql = f.read()
            
        print("Executing schema.sql...")
        # Split by semicolon and filter out empty strings
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        for statement in statements:
            try:
                cursor.execute(statement)
            except mysql.connector.Error as err:
                print(f"Warning executing statement: {err}")
                
        print("Database and tables created successfully.")
        
        # Read and execute seed.sql
        print("Reading seed.sql...")
        with open('database/seed.sql', 'r') as f:
            seed_sql = f.read()
            
        print("Executing seed.sql...")
        statements = [s.strip() for s in seed_sql.split(';') if s.strip()]
        for statement in statements:
            try:
                cursor.execute(statement)
            except mysql.connector.Error as err:
                # Ignore duplicate entry errors for seed data
                if err.errno == 1062:
                    pass
                else:
                    print(f"Warning executing seed statement: {err}")
            
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Setup complete! You can now run 'python app.py'.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except FileNotFoundError as err:
        print(f"Error: Could not find SQL file. {err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

if __name__ == '__main__':
    init_db()
