#!/usr/bin/env python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator to yield users in batches from the user_data table"""
    conn = mysql.connector.connect(
        host="localhost",
        user="your_username",       # Replace with your MySQL username
        password="your_password",   # Replace with your MySQL password
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        yield rows

    cursor.close()
    conn.close()

def batch_processing(batch_size):
    """Generator to yield users over age 25 in batches"""
    for batch in stream_users_in_batches(batch_size):
        yield [user for user in batch if float(user['age']) > 25]
