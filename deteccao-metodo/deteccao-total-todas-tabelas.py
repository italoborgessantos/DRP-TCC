import pymysql
import boto3
import os
from datetime import datetime
import sys
from dotenv import load_dotenv
import os

load_dotenv()

LOG_FILE = "/home/ubuntu/deteccao/rto_log.txt"
LOCKFILE = "/tmp/detect_attack.lock"


DETECTION_FIELD = 'is_encrypted'
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def escreve_log(mensagem: str):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    linha = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensagem}\n"

    with open(LOG_FILE, "a") as arquivo:
        arquivo.write(linha)


def obtain_connection():
    db_host = boto3.client(
        "ssm",
        region_name="us-east-1"
    ).get_parameter(
        Name="/app/db/endpoint",
        WithDecryption=False
    )['Parameter']['Value']

    return pymysql.connect(
        host=db_host,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def get_detection_tables(cursor):
    cursor.execute(
        """
        SELECT TABLE_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
          AND COLUMN_NAME = %s
        """,
        (DB_NAME, DETECTION_FIELD)
    )

    rows = cursor.fetchall()

    table_fields = {}

    for row in rows:
        table_fields[row['TABLE_NAME']] = row['COLUMN_NAME']

    return table_fields


# Evita múltiplas execuções simultâneas
if os.path.exists(LOCKFILE):
    escreve_log("Detect script already running — abortando.")
    sys.exit(0)

with open(LOCKFILE, "w") as f:
    f.write(str(os.getpid()))

conn = None

try:
    conn = obtain_connection()

    with conn.cursor() as cur:

        escreve_log(
            "Detector (agregado) iniciado — consultando DB inteiro via SQL em todas as tabelas."
        )

        table_fields = get_detection_tables(cur)

        total_suspeitos = 0
        total_registros = 0

        if not table_fields:
            escreve_log(
                f"Nenhuma tabela com a coluna '{DETECTION_FIELD}' encontrada."
            )

        for table, field in table_fields.items():

            query = f"""
                SELECT
                    SUM(CASE WHEN `{field}` = 1 THEN 1 ELSE 0 END) AS suspeitos,
                    COUNT(*) AS total
                FROM `{table}`
            """

            cur.execute(query)

            resultado = cur.fetchone()

            suspeitos = int(resultado['suspeitos'] or 0)
            tabela_total = int(resultado['total'] or 0)

            total_suspeitos += suspeitos
            total_registros += tabela_total

            escreve_log(
                f"Tabela {table}: {suspeitos}/{tabela_total} registros suspeitos."
            )

        proporcao = (
            total_suspeitos / total_registros
            if total_registros > 0
            else 0.0
        )

        if proporcao > 0.6:
            escreve_log(
                f"Proporção suspeita detectada: "
                f"{proporcao:.4f} "
                f"({total_suspeitos} de {total_registros})"
            )
        else:
            escreve_log(
                f"Proporção normal: "
                f"{proporcao:.4f} "
                f"({total_suspeitos} de {total_registros})"
            )

    cloudwatch = boto3.client(
        'cloudwatch',
        region_name='us-east-1'
    )

    cloudwatch.put_metric_data(
        Namespace='App/Ransomware',
        MetricData=[
            {
                'MetricName': 'DadosCriptografados',
                'Value': proporcao,
                'Unit': 'None'
            }
        ]
    )

    escreve_log(
        f"Métrica enviada ao CloudWatch: DadosCriptografados={proporcao:.4f}"
    )

except Exception as e:
    escreve_log(f"[ERRO] {str(e)}")
    raise

finally:
    if conn:
        try:
            conn.close()
        except:
            pass

    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)
