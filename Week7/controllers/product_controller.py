from flask import Blueprint, request, jsonify
from services.product_service import ProductService

product_bp = Blueprint('product_bp', __name__)
product_service = ProductService()

def format_error(message, code):
    """Định dạng Error Response."""
    return {"message": message, "code": code}

@product_bp.route('', methods=['GET'])
def get_products():
    skip = request.args.get('skip', 0)
    limit = request.args.get('limit', 10)
    search = request.args.get('search', None)
    
    try:
        products = product_service.get_products(skip, limit, search)
        return jsonify(products), 200
    except ValueError as e:
        return jsonify(format_error(str(e), 400)), 400
    except Exception as e:
        return jsonify(format_error(str(e), 500)), 500

@product_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = product_service.get_product(product_id)
        return jsonify(product), 200
    except KeyError as e:
        return jsonify(format_error(str(e).strip("'"), 404)), 404
    except Exception as e:
        return jsonify(format_error(str(e), 500)), 500

@product_bp.route('', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data:
        return jsonify(format_error("Invalid input", 400)), 400
        
    try:
        product = product_service.create_product(data)
        return jsonify(product), 201
    except ValueError as e:
        return jsonify(format_error(str(e), 400)), 400
    except Exception as e:
        return jsonify(format_error(str(e), 500)), 500

@product_bp.route('/<product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    if not data:
        return jsonify(format_error("Invalid input", 400)), 400
        
    try:
        product = product_service.update_product(product_id, data)
        return jsonify(product), 200
    except ValueError as e:
        return jsonify(format_error(str(e), 400)), 400
    except KeyError as e:
        return jsonify(format_error(str(e).strip("'"), 404)), 404
    except Exception as e:
        return jsonify(format_error(str(e), 500)), 500

@product_bp.route('/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product_service.delete_product(product_id)
        return '', 204
    except KeyError as e:
        return jsonify(format_error(str(e).strip("'"), 404)), 404
    except Exception as e:
        return jsonify(format_error(str(e), 500)), 500