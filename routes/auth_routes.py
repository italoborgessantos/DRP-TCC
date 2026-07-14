from flask import Blueprint, request, jsonify
from services.auth_services import create_employee, login_employee

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/auth', methods=['POST'])
def create_emp():
    try:
        data = request.get_json()
        if "name" not in data or "email" not in data:
            return jsonify({"error": "Nome e e-mail são obrigatórios"}), 400

        response, status_code = create_employee(data)
        return jsonify(response), status_code
    except Exception as e:
        print(f"Erro ao criar funcionário: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    response, status_code = login_employee(data)
    return jsonify(response), status_code
