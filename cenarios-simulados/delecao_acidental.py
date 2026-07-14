import pymysql
from dotenv import load_dotenv
import os


# CONFIGURAÇÕES


TABLE = "order_products"
DELETE_PERCENT = 0.50  # 50%


# CONEXÃO COM RDS


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False
)

try:

    with connection.cursor() as cursor:

        cursor.execute(f"SELECT COUNT(*) AS total FROM {TABLE}")
        total = cursor.fetchone()["total"]

        delete_rows = int(total * DELETE_PERCENT)

        print(f"Registros atuais: {total}")
        print(f"Removendo {delete_rows} registros...")

        cursor.execute(f"""
            DELETE FROM {TABLE}
            ORDER BY id DESC
            LIMIT {delete_rows}
        """)

    connection.commit()

    print("Deleção acidental simulada com sucesso.")

except Exception as e:

    connection.rollback()
    print(e)

finally:

    connection.close()
