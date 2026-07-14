from flask import Blueprint, request, jsonify

from auth.authenticate import jwt_required
from services.product_services import *

product_bp = Blueprint('product_bp', __name__)


@product_bp.route('/products', methods=['POST'])
@jwt_required
def create(current_employee):
    data = request.json
    response, status_code = create_product(data)
    return jsonify(response), status_code


@product_bp.route('/products', methods=['GET'])
@jwt_required
def get_all(current_employee):
    limit = min(request.args.get("limit", 10, type=int), 100)
    offset = request.args.get("offset", 0, type=int)

    response, status_code = get_all_products(limit, offset)
    return jsonify(response), status_code


@product_bp.route('/products/<string:product_name>', methods=['GET'])
@jwt_required
def get(current_employee, product_name):
    response, status_code = get_product(product_name)
    return jsonify(response), status_code


@product_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required
def get_by_id(current_employee, product_id):
    response, status_code = get_product_by_id(product_id)
    return jsonify(response), status_code


@product_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required
def update(current_employee, product_id):
    data = request.json
    updated_product, status_code = update_product(product_id, data)
    return jsonify(updated_product), status_code


@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required
def delete(current_employee, product_id):
    deleted_product, status_code = delete_product(product_id)
    return jsonify(deleted_product), status_code
