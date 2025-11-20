import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="user_name",
        password="mysql_password",
        database="DB_name"
    )

    
