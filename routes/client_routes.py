from flask import Blueprint, request, jsonify

from services.client_services import *
from auth.authenticate import jwt_required

client_bp = Blueprint('client_bp', __name__)


@client_bp.route('/clients', methods=['POST'])
@jwt_required
def create(current_employee):
    data = request.get_json()
    if "name" not in data or "email" not in data:
        return jsonify({"error": "Nome e e-mail são obrigatórios"}), 400

    response, status_code = create_client(data)
    return jsonify(response), status_code


@client_bp.route('/clients', methods=['GET'])
@jwt_required
def get_all(current_employee):
    limit = min(request.args.get("limit", 10, type=int), 100)
    offset = request.args.get("offset", 0, type=int)

    response, status_code = get_all_clients(limit, offset)
    return jsonify(response), status_code


@client_bp.route('/clients/<int:client_id>', methods=['PUT'])
@jwt_required
def update(current_employee, client_id):
    data = request.get_json()
    updated_client, status_code = update_client(client_id, data)
    return jsonify(updated_client), status_code


@client_bp.route('/clients/<int:client_id>', methods=['DELETE'])
@jwt_required
def delete(current_employee, client_id):
    deleted_user, status_code = delete_client(client_id)
    return jsonify(deleted_user), status_code


@client_bp.route('/clients/<string:name>/<string:email>', methods=['GET'])
@jwt_required
def get(current_employee, name, email):
    client, status_code = get_client(name, email)
    # print("current_client: ", current_client)
    return jsonify(client), status_code


@client_bp.route('/clients/<int:client_id>', methods=['GET'])
@jwt_required
def get_by_id(current_employee, client_id):
    client, status_code = get_client_by_id(client_id)
    return jsonify(client), status_code
