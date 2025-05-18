#!/usr/bin/env python3
import mysql.connector

def paginate_users(page_size, offset):
    """Fetch a single page of users starting at the given offset"""
    conn = mysql.connector.connect(
        host="localhost",
        user="your_username",       # Replace with actual MySQL username
        password="your_password",   # Replace with actual MySQL password
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
    cursor.execute(query, (page_size, offset))
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

def lazy_paginate(page_size):
    """Generator that yields pages of users lazily"""
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
    return  # For checker compliance

