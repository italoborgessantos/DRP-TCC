from services.product_services import update_product
from models.orderproducts import OrderProduct
from models.products import Product
from models.client import Client
from models.database import db


def make_order(data):
    client = Client.query.get(data['client_id'])
    product = Product.query.get(data['product_id'])

    if not client or not product:
        return {"erro": "Cliente ou produto não encontrado!"}, 404

    if product.stock < data['quantity']:
        return {"erro": "Produto sem o estoque necessário para o pedido!!"}, 400

    order = OrderProduct(
        order_client=client.id,
        order_product=product.id,
        order_quantity=data['quantity'],

    )

    try:
        db.session.add(order)
        db.session.commit()
        new_quantity = product.stock - data['quantity']
        product.stock = new_quantity
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"erro": f"Erro ao criar pedido: {str(e)}"}, 500

    return order.to_dict(), 201


def get_orders(limit, offset):
    orders = OrderProduct.query.limit(limit).offset(offset).all()
    resultado = []
    for order in orders:
        resultado.append({
            "id": order.id,
            "order_client": order.order_client,
            "client_name": order.order.name,
            "order_product": order.order_product,
            "product_name": order.product.name,
            "description": order.description,
            "quantity": order.order_quantity,
            "order_date": order.order_date.isoformat()
        })
    return resultado, 200


def get_order_by_id(order_id):
    order = OrderProduct.query.get(order_id)
    if not order:
        return {"erro": "Pedido não encontrado!"}, 404
    return order.to_dict(), 200


def update_order(order_id, data):
    order = OrderProduct.query.get(order_id)
    if not order:
        return {"erro": "Pedido não encontrado!"}, 404

    if 'client_id' in data:
        client = Client.query.get(data['client_id'])
        if not client:
            return {"erro": "Cliente não encontrado!"}, 404
        order.order_client = client.id

    if 'product_id' in data:
        product = Product.query.get(data['product_id'])
        if not product:
            return {"erro": "Produto não encontrado!"}, 404
        order.order_product = product.id

    if 'quantity' in data:
        order.order_quantity = data['quantity']

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"erro": f"Erro ao atualizar pedido: {str(e)}"}, 500

    return order.to_dict(), 200


def delete_order(order_id):
    order = OrderProduct.query.get(order_id)
    product = Product.query.get(order.order_product)
    if not order:
        return {"erro": "Pedido não encontrado!"}, 404

    try:
        db.session.delete(order)
        new_quantity = product.stock+order.order_quantity
        product.stock = new_quantity
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"erro": f"Erro ao deletar pedido: {str(e)}"}, 500

    return {"message": "Pedido deletado com sucesso!"}, 200
