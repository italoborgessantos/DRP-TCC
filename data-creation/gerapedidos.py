import random
from faker import Faker
import mysql.connector

fake = Faker()

# Configurações
num_clientes = 50000
num_produtos = 100000
total_registros = 8160000
batch_size = 10000  # você pode reduzir para 5000 se quiser testar antes

# Conexão com o banco
conn = mysql.connector.connect(
    host="172.30.95.209",
    user="root",
    password="emp280556.",
    database="db_shop"
)
cursor = conn.cursor()

# Desabilita constraints temporariamente para melhorar performance
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
print("Constraints temporariamente desativadas.")

# Criação da tabela, se necessário
cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_client INT NOT NULL,
        order_product INT NOT NULL,
        order_quantity INT NOT NULL DEFAULT 1,
        order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_client) REFERENCES clients(id),
        FOREIGN KEY (order_product) REFERENCES products(id)
    )
""")
print("Tabela `order_products` verificada/criada com sucesso.")

# Geração e inserção em batches
print("Iniciando inserções em lote...")
for i in range(0, total_registros, batch_size):
    dados = []
    for _ in range(batch_size):
        cliente_id = random.randint(1, num_clientes)
        produto_id = random.randint(1, num_produtos)
        quantidade = random.randint(1, 5)
        data_pedido = fake.date_time_this_year()
        dados.append((cliente_id, produto_id, quantidade, data_pedido))

    cursor.executemany("""
        INSERT INTO order_products (order_client, order_product, order_quantity, order_date)
        VALUES (%s, %s, %s, %s)
    """, dados)

    conn.commit()
    print(f"Lote {i // batch_size + 1} inserido ({i + batch_size} registros)...")

# Reabilita constraints
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
print("Constraints reativadas.")

cursor.close()
conn.close()
print("Finalizado com sucesso.")
