import pymysql

try:
    connection = pymysql.connect(host='localhost', user='root', password='')
    cursor = connection.cursor()
    cursor.execute("DROP DATABASE IF EXISTS shopkeeper")
    cursor.execute("CREATE DATABASE shopkeeper")
    print("Database recreated successfully.")
    connection.close()
except Exception as e:
    print(f"Error recreating database: {e}")
