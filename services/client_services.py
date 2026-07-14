from models.client import Client
from models.database import db


def create_client(data):
    if Client.query.filter_by(email=data['email']).first():

        return {"erro": "E-mail já cadastrado!"}, 400

    new_client = Client(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone') or None,
        address=data.get('address') or None

    )
    try:
        db.session.add(new_client)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return {"erro": f"Erro ao criar usuário: {str(e)}"}, 500

    return get_client(new_client.name, new_client.email), 201


def get_all_clients(limit, offset):
   # all_clients = Client.query.all()
    all_clients = Client.query.limit(limit).offset(offset).all()
    return list(client.to_dict() for client in all_clients), 200


def get_client(c_name, c_email):
    client = Client.query.filter_by(name=c_name, email=c_email).first()
    if not client:
        return {"erro": "Usuário não encontrado!"}, 404

    return client.to_dict(), 200


def get_client_by_id(client_id):
    client = Client.query.get(client_id)
    if not client:
        return {"erro": "Usuário não encontrado!"}, 404
    return client.to_dict(), 200


def update_client(client_id, data):
    client = Client.query.get(client_id)
    if not client:
        return {"erro": "Usuário não encontrado!"}, 404

    client.name = data.get('name', client.name) or None
    client.email = data.get('email', client.email) or None
    client.phone = data.get('phone', client.phone) or None
    client.address = data.get('address', client.address) or None

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"erro": f"Erro ao editar usuário: {str(e)}"}, 500

    return client.to_dict(), 200


def delete_client(id):
    client = Client.query.get(id)
    if not client:
        return {"erro": "Usuário não encontrado!"}, 404

    try:
        db.session.delete(client)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"erro": f"Erro ao deletar usuário: {str(e)}"}, 500

    return client.to_dict(), 200
