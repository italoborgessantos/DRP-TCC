import pymysql
import boto3
import os
from datetime import datetime
import sys
import math
from dotenv import load_dotenv
import os

load_dotenv()

ALERT_THRESHOLD = 0.6
LOG_FILE = "/home/ubuntu/deteccao/rto_log.txt"
LOCKFILE = "/tmp/detect_attack.lock"
STATE_FILE_TEMPLATE = "/tmp/detect_last_id_{table}.txt"
FRACTION = 0.25
DETECTION_FIELDS = ['is_encrypted']


DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def escreve_log(mensagem: str):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    linha = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensagem}\n"
    with open(LOG_FILE, "a") as arquivo:
        arquivo.write(linha)


def is_detect_script_running():
    if os.path.exists(LOCKFILE):
        try:
            with open(LOCKFILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            return False
    return False


def get_all_tables(cursor):
    cursor.execute(
        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'",
        ('db_shop',)
    )
    return [row['TABLE_NAME'] for row in cursor.fetchall()]


def get_detection_field(cursor, table_name):
    cursor.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
        ('db_shop', table_name)
    )
    columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
    if 'id' not in columns:
        return None
    for field in DETECTION_FIELDS:
        if field in columns:
            return field
    return None


def get_table_row_count(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) AS total FROM `{table_name}`")
    return cursor.fetchone()['total']


def read_last_id(table_name):
    state_file = STATE_FILE_TEMPLATE.format(table=table_name)
    if not os.path.exists(state_file):
        return 0
    with open(state_file, 'r') as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0


def save_last_id(table_name, last_id):
    state_file = STATE_FILE_TEMPLATE.format(table=table_name)
    with open(state_file, 'w') as f:
        f.write(str(last_id))


def scan_table(cursor, table_name, detection_field, page_size, last_id):
    cursor.execute(
        f"SELECT id, `{detection_field}` FROM `{table_name}` "
        "WHERE id > %s ORDER BY id ASC LIMIT %s",
        (last_id, page_size)
    )
    rows = cursor.fetchall()
    if not rows:
        cursor.execute(
            f"SELECT id, `{detection_field}` FROM `{table_name}` "
            "ORDER BY id ASC LIMIT %s",
            (page_size,)
        )
        rows = cursor.fetchall()
    return rows


if is_detect_script_running():
    escreve_log("[ABORTADO] Script detect_attack.py já em execução.")
    sys.exit(0)

with open(LOCKFILE, "w") as f:
    f.write(str(os.getpid()))

try:
    db_host = boto3.client("ssm", region_name="us-east-1").get_parameter(
        Name="/app/db/endpoint", WithDecryption=False)['Parameter']['Value']

    connection = pymysql.connect(
        host=db_host,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with connection.cursor() as cursor:
        tables = get_all_tables(cursor)
        total_database_rows = 0
        table_infos = []

        for table in tables:
            row_count = get_table_row_count(cursor, table)
            total_database_rows += row_count
            detection_field = get_detection_field(cursor, table)
            table_infos.append((table, row_count, detection_field))

        PAGE_SIZE = max(500, math.ceil(total_database_rows * FRACTION))
        escreve_log(
            f"Total de tabelas: {len(tables)} | Registros totais em todas as tabelas: {total_database_rows} | Lote: {PAGE_SIZE}")

        total_suspeitos = 0
        total_lidos = 0

        for table, row_count, detection_field in table_infos:
            if not detection_field:
                escreve_log(
                    f"Tabela {table}: {row_count} registros, sem campo de detecção. Pulando.")
                continue

            last_id = read_last_id(table)
            rows = scan_table(cursor, table, detection_field,
                              PAGE_SIZE, last_id)
            if rows:
                save_last_id(table, rows[-1]['id'])
                suspeitos = sum(1 for row in rows if row[detection_field])
                total_suspeitos += suspeitos
                total_lidos += len(rows)
                escreve_log(
                    f"Tabela {table}: lidos {len(rows)} registros, campo '{detection_field}', suspeitos {suspeitos}.")
            else:
                escreve_log(
                    f"Tabela {table}: nenhum registro encontrado para leitura.")

        proporcao = total_suspeitos / total_database_rows if total_database_rows else 0

        if proporcao > ALERT_THRESHOLD:
            escreve_log(
                f"[ALERTA] Proporção suspeita: {proporcao:.2f} ({total_suspeitos}/{total_database_rows})")
        else:
            escreve_log(
                f"Proporção normal: {proporcao:.2f} ({total_suspeitos}/{total_database_rows})")

        boto3.client('cloudwatch', region_name='us-east-1').put_metric_data(
            Namespace='App/Ransomware',
            MetricData=[{
                'MetricName': 'DadosCriptografados',
                'Value': proporcao,
                'Unit': 'None'
            }]
        )

except Exception as e:
    escreve_log(f"[ERRO] {str(e)}")
finally:
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)
