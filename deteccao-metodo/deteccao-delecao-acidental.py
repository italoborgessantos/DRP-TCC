import pymysql
import boto3
import json
import os
from dotenv import load_dotenv
from datetime import datetime


# CONFIGURAÇÕES


TABLE = "order_products"

STATE_FILE = "/home/ubuntu/shopee/record_count.json"

THRESHOLD = 0.40

NAMESPACE = "App/Deletion"
METRIC_NAME = "DeletedRecords"


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

cloudwatch = boto3.client(
    "cloudwatch",
    region_name=""
)

try:

    with connection.cursor() as cursor:

        cursor.execute(f"SELECT COUNT(*) AS total FROM {TABLE}")
        current_count = cursor.fetchone()["total"]

finally:

    connection.close()

# Primeira execução
if not os.path.exists(STATE_FILE):

    with open(STATE_FILE, "w") as file:

        json.dump(
            {
                "count": current_count
            },
            file
        )

    print("Baseline criada.")
    exit()

# Leitura da última verificação
with open(STATE_FILE, "r") as file:

    previous_count = json.load(file)["count"]

difference = previous_count - current_count
loss_percentage = difference / previous_count

print("-------------------------------------")
print(f"Horário: {datetime.now()}")
print(f"Anterior : {previous_count}")
print(f"Atual    : {current_count}")
print(f"Perda    : {loss_percentage*100:.2f}%")
print("-------------------------------------")

# Detecção
if loss_percentage >= THRESHOLD:

    print("Deleção acidental detectada!")

    cloudwatch.put_metric_data(
        Namespace=NAMESPACE,
        MetricData=[
            {
                "MetricName": METRIC_NAME,
                "Value": loss_percentage,
                "Unit": "Percent"

            }
        ]
    )

else:

    print("Nenhuma deleção significativa detectada.")

# Atualiza referência
with open(STATE_FILE, "w") as file:

    json.dump(
        {
            "count": current_count
        },
        file
    )
