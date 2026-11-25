# Use .env variables to establish a connection to MySQL via a function 
import mysql.connector
from fastapi import HTTPException
from configuration.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def get_connection():
    try:
        return mysql.connector.connect(
            host = DB_HOST,
            port = DB_PORT,
            user = DB_USER,
            password = DB_PASSWORD,
            database = DB_NAME,
        )

    # If MySQL is unavailable, return a 503 error and a message
    except mysql.connector.Error:
            raise HTTPException(
                status_code = 503,
                detail = "Database unavailable"
            )
