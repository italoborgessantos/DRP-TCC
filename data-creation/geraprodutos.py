from faker import Faker
import mysql.connector
import random

fake = Faker()

# Conexão com o banco de dados
conn = mysql.connector.connect(
    host="172.30.95.209",
    user="root",
    password="emp280556.",
    database="db_shop"
)
cursor = conn.cursor()

# Criação da tabela products
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        stock INT NOT NULL DEFAULT 0,
        name VARCHAR(200) NOT NULL UNIQUE,
        price FLOAT NOT NULL,
        description VARCHAR(200),
        category VARCHAR(45)
    )
""")
print("Tabela `products` verificada/criada com sucesso.")

# Inserção dos dados
categorias = ['Eletrônicos', 'Livros', 'Vestuário', 'Alimentos', 'Brinquedos']

for _ in range(100000):  # ajuste a quantidade conforme necessário
    stock = random.randint(5, 100)
    name = f"{fake.word().capitalize()} {fake.word().capitalize()} {random.randint(100000, 999999)}"
    price = round(random.uniform(10.0, 500.0), 2)
    description = fake.sentence(nb_words=8)[:200]
    category = random.choice(categorias)

    query = """
        INSERT INTO products (stock, name, price, description, category)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (stock, name, price, description, category))

conn.commit()
print("Dados inseridos com sucesso na tabela `products`.")

cursor.close()
conn.close()
print("Conexão encerrada.")
