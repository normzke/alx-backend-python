#!/usr/bin/env python3
import mysql.connector

def stream_users():
    """Generator function to fetch users row by row from user_data table"""
    conn = mysql.connector.connect(
        host="localhost",
        user="your_username",     # Replace with your MySQL username
        password="your_password", # Replace with your MySQL password
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    for row in cursor:
        yield row

    cursor.close()
    conn.close()
 
