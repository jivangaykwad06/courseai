import mysql.connector

from mysql.connector import pooling

from config import Config


pool = pooling.MySQLConnectionPool(

    pool_name="courseai_pool",

    pool_size=5,

    pool_reset_session=True,

    host=Config.MYSQL_HOST,

    port=Config.MYSQL_PORT,

    user=Config.MYSQL_USER,

    password=Config.MYSQL_PASSWORD,

    database=Config.MYSQL_DATABASE,

    charset="utf8mb4",

    collation="utf8mb4_unicode_ci"
)


def get_connection():

    return pool.get_connection()