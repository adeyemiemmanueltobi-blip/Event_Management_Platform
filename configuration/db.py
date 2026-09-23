from config import config
import pymysql

def get_connection():
    connection = pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        database="learning_platform",   # ← put the real name here
        cursorclass=pymysql.cursors.DictCursor
    )
    
    return connection