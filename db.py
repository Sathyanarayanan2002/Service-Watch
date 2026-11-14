import mysql.connector
import os


def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "servicewatch"),
        port=int(os.getenv("MYSQL_PORT", "3306"))
    )

    return connection