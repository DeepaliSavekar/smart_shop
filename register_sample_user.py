import mysql.connector
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def register_user():
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME', 'smartshopping')
    }

    try:
        # Connect to the database
        print(f"Connecting to database: {db_config['host']}...")
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        
        # User details
        email = "sample@example.com"
        password = "Password@123"
        name = "Demo User"
        phone = "9876543210"

        # Check if user already exists
        print(f"Checking if user '{email}' exists...")
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"User with email '{email}' already exists.")
            return

        # Hash the password
        print("Hashing password...")
        hashed_password = generate_password_hash(password)

        # Insert user
        print("Inserting new user...")
        query_user = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_user, (name, email, phone, hashed_password))
        
        # Get the new user's ID
        user_id = cursor.lastrowid
        print(f"User created with ID: {user_id}")

        # Create wallet for the new user
        print("Creating wallet for user...")
        query_wallet = "INSERT INTO wallet (user_id, balance) VALUES (%s, 0.00)"
        cursor.execute(query_wallet, (user_id,))
        
        # Commit changes
        db.commit()
        print("✅ User registered successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")

    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()
            print("Database connection closed.")

if __name__ == "__main__":
    register_user()
