#!/usr/bin/env python3
import mysql.connector

def connect_to_prodev():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Replace with your actual password
        database="ALX_prodev"
    )

def stream_user_ages():
    conn = connect_to_prodev()
    cursor = conn.cursor()
    cursor.execute("SELECT age FROM user_data;")
    for (age,) in cursor:
        yield age
    cursor.close()
    conn.close()

def compute_average_age():
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1

    if count == 0:
        print("No users found.")
    else:
        print(f"Average age of users: {total_age / count:.2f}")

if __name__ == "__main__":
    compute_average_age()

