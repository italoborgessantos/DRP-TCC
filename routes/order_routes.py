from flask import Blueprint, request, jsonify
from auth.authenticate import jwt_required
from services.order_services import *

order_bp = Blueprint('order_bp', __name__)


@order_bp.route('/orders', methods=['POST'])
@jwt_required
def order(current_employee):
    data = request.json
    if not data:
        return {"erro": "Requisição inválida!"}, 400
    response, status = make_order(data)
    return jsonify(response), status


@order_bp.route('/orders', methods=['GET'])
@jwt_required
def orders(current_employee):
    limit = min(request.args.get("limit", 10, type=int), 100)
    offset = request.args.get("offset", 0, type=int)

    response, status = get_orders(limit, offset)

    return jsonify(response), status


@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required
def order_id(current_employee, order_id):
    response, status = get_order_by_id(order_id)
    return jsonify(response), status


@order_bp.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required
def order_update(current_employee, order_id):
    data = request.json
    if not data:
        return {"erro": "Requisição inválida!"}, 400
    response, status = update_order(order_id, data)
    return jsonify(response), status


@order_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required
def order_delete(current_employee, order_id):
    response, status = delete_order(order_id)
    return jsonify(response), status
