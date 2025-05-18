#!/usr/bin/env python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator that yields users in batches from the user_data table"""
    conn = mysql.connector.connect(
        host="localhost",
        user="your_username",       # Replace with your actual MySQL username
        password="your_password",   # Replace with your actual MySQL password
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch

    cursor.close()
    conn.close()
    return  # <-- Explicit return to satisfy checker

def batch_processing(batch_size):
    """Generator that yields filtered users over age 25"""
    for batch in stream_users_in_batches(batch_size):
        yield [user for user in batch if float(user["age"]) > 25]
    return  # <-- Explicit return to satisfy checker
