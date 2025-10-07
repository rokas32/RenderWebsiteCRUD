# app.py

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# --- Configuration ---
app = Flask(__name__)

# When deployed on Render, it will ALWAYS use the values set in the Environment tab first.

# You must replace 'YOUR_DEFAULT_...' with the actual values you extracted from the Render Internal URL
DB_HOST = os.environ.get('DB_HOST', 'dpg-d3ic7qje5dus7390s4gg-a')
DB_NAME = os.environ.get('DB_NAME', 'product_db_k4v2')
DB_USER = os.environ.get('DB_USER', 'product_db_k4v2_user')
DB_PASS = os.environ.get('DB_PASS', 'RT2RIIydmEMUrdzAgvOsF3YNH2rwpCfr')

# --- Connection Test Route ---
@app.route('/')
def connection_test():
    # If the variables are NOT set on Render AND you haven't replaced the YOUR_DEFAULT placeholders:
    if 'YOUR_DEFAULT' in DB_HOST or 'YOUR_DEFAULT' in DB_PASS:
        return '<h1>Configuration Error!</h1><p>You must set the DB_HOST, DB_NAME, DB_USER, and DB_PASS variables on the Render dashboard AND/OR replace the "YOUR_DEFAULT_..." placeholders in app.py.</p>', 500


    # Check if any required variable is missing (meaning they were not set on Render)
    # This check is mainly for when we don't set fallbacks or need to know if Render provided them
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
        # This part will be reached if any value is an empty string
        return '<h1>Connection Test FAILED! ❌</h1><p>Configuration missing, check environment variables.</p>', 500
    
    conn = None
    try:
        # Attempt to establish a connection using individual parameters
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        
        # If connection succeeds
        conn.close() 
        return '<h1>Connection Test SUCCESS! 🎉</h1><p>Flask is running AND successfully connected to the PostgreSQL database using individual parameters.</p>', 200
        
    except Exception as e:
        # Connection failed despite having all variables (this means credentials are bad)
        return f'<h1>Connection Test FAILED! ❌</h1><p>Flask is running, but could not connect to PostgreSQL. (Variables are set, but credentials are wrong)</p><p>Detail: <strong>{e}</strong></p><p><strong>Host used: {DB_HOST}</strong></p>', 500
    
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
    
    
# --- Entity Model: Product (The table structure) ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # 1. String: name 
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    
    # 2. Float/Decimal: price 
    price = db.Column(db.Float, default=0.00) 
    
    # 3. Integer: stock_quantity
    stock_quantity = db.Column(db.Integer, default=0) 
    
    # 4. Boolean: is_available 
    is_available = db.Column(db.Boolean, default=True) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': f"{self.price:.2f}",
            'stock_quantity': self.stock_quantity,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat()
        }

# Initial database creation (This creates the table on Render deployment)
with app.app_context():
    # If the database connection fails here, the app deployment will fail, which is correct.
    try:
        db.create_all()
        print("Database tables created successfully or already exist.")
    except Exception as e:
        print(f"ERROR: Failed to create database tables. Check connection details. Error: {e}")

# --- Helper for Input Validation (Checks 4 Data Types) ---
def validate_product_input(data):
    # (Validation function remains the same as previously defined)
    
    # Check 1: String type (Name must be a non-empty string)
    name = data.get('name')
    if name is not None:
        if not isinstance(name, str) or not name.strip():
            return "Name must be a non-empty string.", 400
            
    # Check 2: Float type (Price must be a number >= 0)
    price = data.get('price')
    if price is not None:
        try:
            price = float(price)
            if price < 0:
                 return "Price cannot be negative.", 400
        except (TypeError, ValueError):
            return "Price must be a valid number.", 400
            
    # Check 3: Integer type (Stock Quantity must be a non-negative integer)
    stock_quantity = data.get('stock_quantity')
    if stock_quantity is not None:
        try:
            if isinstance(stock_quantity, float) and stock_quantity != int(stock_quantity):
                return "Stock quantity must be a whole number (integer).", 400
            
            stock_quantity = int(stock_quantity) 
            
            if stock_quantity < 0:
                return "Stock quantity cannot be negative.", 400
        except Exception:
            return "Stock quantity must be a valid integer.", 400

    # Check 4: Boolean type (is_available must be a boolean)
    is_available = data.get('is_available')
    if is_available is not None and not isinstance(is_available, bool):
        return "is_available must be a boolean (true/false).", 400

    return "Valid", None




# --- CRUD Routes (API Endpoints) ---

# C: Create Product
@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({"error": "Name field is required."}), 400
    
    validation_message, error_code = validate_product_input(data)
    if error_code:
        return jsonify({"error": validation_message}), error_code
        
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
@app.route('/api/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

# R: Read Single Product
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

# U: Update Product
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    validation_message, error_code = validate_product_input(data)
    if error_code:
        return jsonify({"error": validation_message}), error_code
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = float(data['price'])
    if 'stock_quantity' in data:
        product.stock_quantity = int(data['stock_quantity'])
    if 'is_available' in data:
        product.is_available = data['is_available']
    
    db.session.commit()
    return jsonify(product.to_dict())

# D: Delete Product
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Product {product_id} deleted."}), 204

if __name__ == '__main__':
    app.run(debug=True)