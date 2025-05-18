#!/usr/bin/env python3
import csv
import mysql.connector
import uuid


def connect_db():
    """Connect to MySQL server (not to a specific DB yet)"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # <-- Replace with your MySQL password
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_database(connection):
    """Create ALX_prodev database if it doesn't exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        connection.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Database creation failed: {err}")


def connect_to_prodev():
    """Connect to the ALX_prodev database"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # <-- Replace with your MySQL password
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None


def create_table(connection):
    """Create user_data table with specified schema"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL
            )
        """)
        connection.commit()
        cursor.close()
        print("Table user_data created successfully")
    except mysql.connector.Error as err:
        print(f"Table creation failed: {err}")


def insert_data(connection, filename):
    """Insert CSV data into user_data table"""
    try:
        cursor = connection.cursor()

        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_id = str(uuid.uuid4())
                name = row['name']
                email = row['email']
                age = row['age']

                # Check for duplicate email
                cursor.execute("SELECT * FROM user_data WHERE email = %s", (email,))
                if cursor.fetchone() is None:
                    cursor.execute("""
                        INSERT INTO user_data (user_id, name, email, age)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, name, email, age))

        connection.commit()
        cursor.close()
        print("Data inserted successfully")
    except Exception as e:
        print(f"Data insertion failed: {e}")
