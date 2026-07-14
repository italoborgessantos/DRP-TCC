#!/bin/bash

set -e

echo "Verificando e instalando Python..."


sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip

echo "Python instalado com sucesso."

echo "Preparando ambiente virtual..."


python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt


chmod 600 mycerts/private_key.pem
chmod 644 mycerts/certificate.pem

TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

PUBLIC_DNS=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/public-hostname)

HTML_PATH="/home/ubuntu/shopee/static/login.html"
sed -i "s|window.API_URL = .*|window.API_URL = \"https://$PUBLIC_DNS:443/\";|" "$HTML_PATH"

echo "DNS público da instância: $PUBLIC_DNS"


sudo nohup ./venv/bin/python app.py > app.log 2>&1 &
