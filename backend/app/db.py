import time
import psycopg2

def get_connection():
    for i in range(5):
        try:
            return psycopg2.connect(
                host="db",
                database="poll",
                user="user",
                password="pass"
            )
        except Exception as e:
            print("DB not ready, retrying...")
            time.sleep(2)
    raise Exception("Cannot connect to DB")