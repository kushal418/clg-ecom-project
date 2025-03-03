import mysql.connector
from mysql.connector import Error
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Function to connect to MySQL database
def create_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="@12345678",  # Replace with your actual MySQL password
            database="ecommerce"
        )
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return None

# Function to setup the database (creates tables if not exists)
def setup_database():
    conn = create_connection()
    if conn is None:
        return

    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            mobile VARCHAR(20) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    
    # Create admins table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """)

    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            image VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database setup complete!")

# Function to register a new user
def register_user(username, email, mobile, password):
    conn = create_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')  # Hash the password
    
    try:
        cursor.execute("INSERT INTO users (username, email, mobile, password) VALUES (%s, %s, %s, %s)",
                       (username, email, mobile, hashed_password))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Function to verify user login
def login_user(email, password):
    conn = create_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, username, password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if user and bcrypt.check_password_hash(user['password'], password):
        return user
    return None  # Login failed

# Function to verify admin login
def login_admin(email, password):
    conn = create_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, username, password FROM admins WHERE email = %s", (email,))
    admin = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if admin and admin['password'] == password: 
        return admin
    return None  # Login failed
