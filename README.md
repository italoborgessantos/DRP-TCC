# Shopee

Aplicação backend Flask para gestão de clientes, produtos e pedidos, preparada para implantação em AWS.

## Visão geral

A pasta `shopee` contém uma aplicação Flask que expõe APIs REST e serve páginas estáticas de administração. O projeto está orientado a rodar em instância EC2 com banco de dados RDS e integração com SSM/Backup.

## Requisitos AWS

- EC2 Ubuntu ou outra distribuição Linux compatível
- RDS MySQL/MariaDB
- IAM com permissões SSM, AWS Backup, CloudWatch Logs
- Chave SSH para acesso à instância
- Certificados em `mycerts/` para HTTPS local na instância (opcional)

## Dependências Python

- Flask
- Flask-Migrate
- Flask-SQLAlchemy
- PyMySQL
- mysql-connector-python
- python-dotenv
- boto3
- pycryptodome

Instale com:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuração de ambiente AWS

O app espera usar o arquivo `lambda_ssm_rds.py` para recuperar a URL do banco via SSM.

A configuração AWS típica inclui:

- `awsbackuppolicy.json` — política IAM para permitir:
  - `ssm:GetParameter`, `ssm:PutParameter`
  - `ssm:SendCommand`
  - `backup:StartRestoreJob`, `backup:DescribeRestoreJob`
  - `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`

- `scriptEC2.sh` — script de bootstrap EC2 que:
  - instala Python e dependências
  - ajusta permissões de certificado
  - recupera `PUBLIC_DNS` via EC2 metadata
  - atualiza `static/login.html` com a URL da API
  - inicializa o app com `nohup`

- `restart_app.sh` — script para reiniciar o app na instância EC2 após restore ou mudança de DNS.

## Variáveis de ambiente

O projeto usa `dotenv` e espera pelo menos:

- `SECRET_KEY`
- `DATABASE_URL` (se `lambda_ssm_rds.py` não estiver disponível)

A configuração local/EC2 de exemplo em `requirementsEC2B.txt` (não recomendado versionar credenciais reais):

```env
DB_USER=admin
DB_PASSWORD=emp280556.
DB_NAME=db_shop
SECRET_KEY='algodificil'
```

Para AWS RDS, a conexão normalmente deve ser gerada via SSM ou `DATABASE_URL`:

```env
DATABASE_URL='mysql+pymysql://usuario:senha@<rds-endpoint>:3306/db_shop'
SECRET_KEY='algodificil'
```

## Configuração do app

Em `app.py`:

- `load_dotenv()` carrega variáveis do ambiente
- `app.config['SECRET_KEY']` usa `SECRET_KEY`
- `app.config['SQLALCHEMY_DATABASE_URI']` chama `get_database_url()` de `lambda_ssm_rds`
- `LOG_FILE_PATH` registra a URL do banco em `/home/ubuntu/shopee/rto_log.txt`

Se você não tiver `lambda_ssm_rds.py`, comente a linha de SSM e use:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
```

## Instruções de implantação AWS

### 1. Preparar EC2

- Lance uma instância EC2 Ubuntu
- Conceda IAM Role com permissões SSM e AWS Backup
- Configure Security Group com porta 8000 aberta para a aplicação e porta 443 se usar HTTPS

### 2. Transferir código

- Faça upload do conteúdo de `shopee` para `/home/ubuntu/shopee`
- Certifique-se que `mycerts/private_key.pem` e `mycerts/certificate.pem` estejam presentes e com permissões corretas

### 3. Executar bootstrap

No EC2:

```bash
cd /home/ubuntu/shopee
bash scriptEC2.sh
```

### 4. Reiniciar após backup/restore

Use `restart_app.sh` quando precisar reiniciar o aplicativo após um restore ou mudança de IP/DNS:

```bash
bash restart_app.sh
```

## Estrutura do projeto

- `app.py` — inicializa Flask, SSM/RDS e Blueprints
- `routes/` — rotas de cliente, produto, pedido e auth
- `services/` — lógica de negócio
- `models/` — entidades ORM e relacionamento
- `static/` — interface de administração estática
- `lambda/` — scripts de recuperação/integridade com AWS Backup e SSM

## Considerações de segurança

- Não commit `requirementsEC2B.txt` nem credenciais reais
- Proteja `mycerts/private_key.pem` com `chmod 600`
- Use role IAM mínimo necessário para a instância EC2
- Use SSM Parameter Store para armazenar credenciais/banco sempre que possível

## Observações finais

- O arquivo `lambda_ssm_rds.py` é necessário para recuperar o endpoint do banco automaticamente via SSM.

