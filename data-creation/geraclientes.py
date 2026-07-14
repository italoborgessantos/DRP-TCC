from faker import Faker
import mysql.connector
from datetime import datetime

fake = Faker()

# Conexão com o banco de dados
conn = mysql.connector.connect(
    host="172.30.95.209",
    user="root",
    password="emp280556.",
    database="db_shop"
)
cursor = conn.cursor()

# Criação da tabela clients
cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        phone VARCHAR(12),
        address VARCHAR(100),
        registered_on DATETIME NOT NULL
    )
""")
print("Tabela `clients` verificada/criada com sucesso.")

# Inserção dos dados
for _ in range(50000):
    name = fake.name()
    email = fake.unique.email()
    phone = fake.phone_number()[:12]
    address = fake.address().replace("\n", ", ")[:100]
    registered_on = datetime.now()

    query = """
        INSERT INTO clients (name, email, phone, address, registered_on)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, email, phone, address, registered_on))

conn.commit()
print("Dados inseridos com sucesso na tabela `clients`.")

cursor.close()
conn.close()
print("Conexão encerrada.")
