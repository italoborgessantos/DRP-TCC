from functools import wraps
import jwt
from flask import request, jsonify, current_app
from models.employee import Employee


def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({'error': 'Não tem permissão!'}), 403

        if not 'Bearer' in token:
            return jsonify({'error': 'Token inválido!'}), 401

        try:
            token_pure = token.replace('Bearer ', '').strip()
            decoded = jwt.decode(
                token_pure, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            employee = Employee.query.filter_by(
                id=decoded['employee_id']).first()
        except Exception as e:
            print(e)
            return jsonify({'error': 'Token inválido!'}), 403

        return f(current_employee=employee, *args, **kwargs)
    return wrapper
