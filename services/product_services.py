from models.products import Product
from models.database import db


def create_product(data):
    if Product.query.filter_by(name=data['name']).first():
        return {"erro": "Produto já cadastrado!"}, 400

    new_product = Product(
        stock=data.get('stock'),
        name=data.get('name'),
        price=data.get('price'),
        description=data.get('description'),
        category=data.get('category')
    )
    try:
        db.session.add(new_product)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return {"erro": f"Erro ao criar produto: {str(e)}"}, 500

    return get_product(new_product.name), 201


def get_all_products(limit, offset):
    # all_products = Product.query.all()
    # return list(product.to_dict() for product in all_products), 200

    products = Product.query.limit(limit).offset(offset).all()
    return list(product.to_dict() for product in products), 200


def get_product(product_name):
    product = Product.query.filter_by(name=product_name).first()
    if not product:
        return {"erro": "Produto não encontrado!"}, 404

    return product.to_dict(), 200


def get_product_by_id(product_id):
    product = Product.query.get(product_id)
    if not product:
        return {"erro": "Produto não encontrado!"}, 404
    return product.to_dict(), 200


def update_product(product_id, data):
    product = Product.query.get(product_id)
    if not product:
        return {"erro": "Produto não encontrado!"}, 404

    product.name = data.get('name', product.name)
    product.stock = data.get('stock', product.stock)
    product.price = data.get('price', product.price)
    product.description = data.get('description', product.description)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"erro": f"Erro ao editar produto: {str(e)}"}, 500

    return product.to_dict(), 200


def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return {"erro": "Produto não encontrado!"}, 404

    try:
        db.session.delete(product)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"erro": f"Erro ao deletar produto: {str(e)}"}, 500

    return product.to_dict(), 200
