import random
from faker import Faker
import mysql.connector
from werkzeug.security import generate_password_hash
from datetime import datetime

# Configurações
fake = Faker()
senha_fixa = "12345678"
senha_hash = generate_password_hash(senha_fixa)

# Conexão com o banco de dados
conn = mysql.connector.connect(
    host="172.30.95.209",
    user="root",
    password="emp280556.",
    database="db_shop"
)
cursor = conn.cursor()

# Criação da tabela employees
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        phone VARCHAR(12),
        registered_on DATETIME NOT NULL,
        password VARCHAR(255) NOT NULL
    )
""")
print("Tabela `employees` verificada/criada com sucesso.")

# Inserção dos dados
for _ in range(1000):  # ajuste o número conforme quiser
    name = fake.name()
    email = fake.unique.email()
    phone = fake.phone_number()[:12]
    registered_on = datetime.now()

    query = """
        INSERT INTO employees (name, email, phone, registered_on, password)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, email, phone, registered_on, senha_hash))

conn.commit()
print("Dados inseridos com sucesso na tabela `employees`.")

cursor.close()
conn.close()
print("Conexão encerrada.")
