from flask import Flask, send_from_directory
import os
from dotenv import load_dotenv
from lambda_ssm_rds import get_database_url
from flask_cors import CORS
from pymysql import DatabaseError

from auth.authenticate import jwt_required
from routes.client_routes import client_bp
from routes.product_routes import product_bp
from routes.order_routes import order_bp
from routes.auth_routes import auth_bp
from models.database import db
LOG_FILE_PATH = "/home/ubuntu/shopee/rto_log.txt"


def create_app():
    app = Flask(__name__)
    CORS(app)

    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    # codigo que roda local
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    # para pegar do SSM o endpoint do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with open(LOG_FILE_PATH, "a") as arquivo:
        arquivo.write(app.config['SQLALCHEMY_DATABASE_URI']+'\n')

    db.init_app(app)

    app.register_blueprint(client_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(auth_bp)

    try:
        with app.app_context():
           # db.drop_all()
            db.create_all()
    except DatabaseError as err:
        if 'already exists' in err._sql_message():
            # db.drop_all()
            # db.create_all()
            print("Databases already exist.")
        else:
            print(err)

    @app.route('/funcionarios')
    def login():
        return send_from_directory('static', 'cadastro.html')

    @app.route('/')
    def home():
        return send_from_directory('static', 'login.html')

    @app.route('/dashboard')
    def dashboard():
        return send_from_directory('static', 'dashboard.html')

    @app.route('/produtos/novo')
    def registro_produtos():
        return send_from_directory('static', 'registro_produtos.html')

    @app.route('/pedidos/novo')
    def registro_pedido():
        return send_from_directory('static', 'registro_pedidos.html')

    @app.route('/clientes/novo')
    def registro_clientes():
        return send_from_directory('static', 'registro_clientes.html')

    @app.route('/produtos')
    def listar_produtos():
        return send_from_directory('static', 'produtos.html')

    @app.route('/clientes')
    def listar_clientes():
        return send_from_directory('static', 'clientes.html')
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8000)
   # app.run(debug=True)
