from services.client_services import get_client
from models.employee import Employee
from models.database import db
from flask import current_app
import jwt
import datetime
from flask import jsonify


def create_employee(data):
    if Employee.query.filter_by(email=data['email']).first():
        return {"error": "Credenciais já cadastradas!", "token": ''}, 400

    new_emp = Employee(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        password=data.get('password'),
    )
    try:
        db.session.add(new_emp)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return {"error": f"Erro ao criar usuário: {str(e)}", "token": ''}, 500

    employee = Employee.query.filter_by(email=data['email']).first()
    if not employee:
        return {"error": "Usuário não encontrado!", "token": ''}, 404

    payload = {
        'employee_id': employee.id,
        'name': employee.name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }

    token = jwt.encode(payload, current_app.config['SECRET_KEY'])

    return {"employee": employee.to_dict(), "token": token}, 201


def login_employee(data):
    employee = Employee.query.filter_by(email=data['email']).first_or_404()
    if not employee.verify_password(data['password']):
        return {"error": "Suas credenciais estão erradas!"}, 403

    payload = {
        'employee_id': employee.id,
        'name': employee.name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }

    token = jwt.encode(payload, current_app.config['SECRET_KEY'])

    return {"token": token}, 200
