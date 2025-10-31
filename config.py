# config.py
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "omi172001"
DB_NAME = "phonepe_pulse"


import mysql.connector as con

def get_connection():
    return con.connect(
        host="localhost",
        user="root",
        password="omi172001",
        database="phonepe_pulse"
    )
