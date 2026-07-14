#!/bin/bash

echo "Reiniciando app Flask..."

cd /home/ubuntu/shopee
sudo pkill -f 'app.py' || echo "Nenhum processo encontrado para matar."

TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

PUBLIC_DNS=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/public-hostname)

HTML_PATH="/home/ubuntu/shopee/static/login.html"
sed -i "s|window.API_URL = .*|window.API_URL = \"https://$PUBLIC_DNS:443/\";|" "$HTML_PATH"

echo "DNS público da instância atualizado para: $PUBLIC_DNS"

source /home/ubuntu/shopee/venv/bin/activate


echo "[$(date '+%Y-%m-%d %H:%M:%S')] [LAMBDA] Banco restaurado com sucesso" | sudo tee -a /home/ubuntu/shopee/rto_log.txt > /dev/null
sudo nohup /home/ubuntu/shopee/venv/bin/python /home/ubuntu/shopee/app.py > /home/ubuntu/shopee/app.log 2>&1 &


echo "App reiniciado com sucesso."
