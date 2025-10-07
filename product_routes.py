# product_routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime
# Note: We do not import db or Product directly here to avoid circular imports.

# 1. Initialize the Blueprint
# We name it 'product_api'
product_api = Blueprint('product_api', __name__)

# --- Helper for Input Validation ---
def validate_product_input(data):
    # (Your full validation function goes here)
    name = data.get('name')
    if name is not None:
        if not isinstance(name, str) or not name.strip():
            return "Name must be a non-empty string.", 400
    price = data.get('price')
    if price is not None:
        try:
            price = float(price)
            if price < 0: return "Price cannot be negative.", 400
        except (TypeError, ValueError): return "Price must be a valid number.", 400
    stock_quantity = data.get('stock_quantity')
    if stock_quantity is not None:
        try:
            if isinstance(stock_quantity, float) and stock_quantity != int(stock_quantity):
                return "Stock quantity must be a whole number (integer).", 400
            stock_quantity = int(stock_quantity) 
            if stock_quantity < 0: return "Stock quantity cannot be negative.", 400
        except Exception: return "Stock quantity must be a valid integer.", 400
    is_available = data.get('is_available')
    if is_available is not None and not isinstance(is_available, bool):
        return "is_available must be a boolean (true/false).", 400
    return "Valid", None


# --- CRUD Routes (using the Blueprint) ---

# C: Create Product
@product_api.route('/products', methods=['POST'])
def create_product():
    # We import the app context variables (db and Product) INSIDE the route
    # to avoid the circular import problem at the top level.
    from app import db, Product 
    
    data = request.get_json()
    if 'name' not in data: return jsonify({"error": "Name field is required."}), 400
    validation_message, error_code = validate_product_input(data)
    if error_code: return jsonify({"error": validation_message}), error_code
        
    new_product = Product(
        name=data['name'],
        description=data.get('description'),
        price=float(data.get('price', 0.00)), 
        stock_quantity=int(data.get('stock_quantity', 0)),
        is_available=data.get('is_available', True)
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201

# R: List All Products
@product_api.route('/products', methods=['GET'])
def list_products():
    from app import Product
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

# R: Read Single Product
@product_api.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    from app import db, Product
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found."}), 404
    return jsonify(product.to_dict())

# U: Update Product
@product_api.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    from app import db, Product
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found."}), 404
        
    data = request.get_json()
    validation_message, error_code = validate_product_input(data)
    if error_code: return jsonify({"error": validation_message}), error_code
    
    if 'name' in data: product.name = data['name']
    if 'description' in data: product.description = data['description']
    if 'price' in data: product.price = float(data['price'])
    if 'stock_quantity' in data: product.stock_quantity = int(data['stock_quantity'])
    if 'is_available' in data: product.is_available = data['is_available']
    
    db.session.commit()
    return jsonify(product.to_dict())

# D: Delete Product
@product_api.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    from app import db, Product
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found."}), 404
        
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Product {product_id} deleted."}), 204