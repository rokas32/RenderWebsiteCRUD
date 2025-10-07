# app.py

import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import the Blueprint containing the CRUD API routes
from product_routes import product_api

# --- Configuration ---
app = Flask(__name__)
# Set a secret key for session management (required for flash messages)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_secret_key_for_flash')
app.url_map.strict_slashes = False 

# Database credentials (These read from Render Environment Variables when deployed)
DB_HOST = os.environ.get('DB_HOST', 'dpg-d3ic7qje2dus7390s4gg-a')
DB_NAME = os.environ.get('DB_NAME', 'product_db_k4v2')
DB_USER = os.environ.get('DB_USER', 'product_db_k4v2_user')
DB_PASS = os.environ.get('DB_PASS', 'RT2RIIydmEMUrdzAgvOsF3YNH2rwpCfr')

# --- SQLALCHEMY SETUP (Connects to DB) ---
# Construct the single connection string (URI)
DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the 'db' object
db = SQLAlchemy(app) 

# --- Entity Model: Product ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, default=0.00) 
    stock_quantity = db.Column(db.Integer, default=0) 
    is_available = db.Column(db.Boolean, default=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Converts the SQLAlchemy model instance to a JSON serializable dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': f"{self.price:.2f}",
            'stock_quantity': self.stock_quantity,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat()
        }

# --- Utility Functions for Form Submission ---
def safe_convert(value, target_type, default):
    """Safely converts a string value to a number type, using default if value is empty/None."""
    if value is None or str(value).strip() == '':
        return default
    try:
        return target_type(value)
    except ValueError:
        raise ValueError(f"Input '{value}' must be a valid number.")


# --- Frontend Routes ---

@app.route('/', methods=['GET'])
def create_product_form():
    """Renders the HTML form (now the root page)."""
    return render_template('create_product.html')

@app.route('/', methods=['POST'])
def submit_product():
    """Handles the form submission and saves the product to the database."""
    
    form_data = request.form
    
    try:
        # 1. Input Cleaning and Conversion
        is_available_val = True if form_data.get('is_available') == 'on' else False
        name_val = form_data.get('name', '').strip()
        description_val = form_data.get('description', '').strip() 
        
        # Safe conversion to prevent ValueError on empty strings
        price_val = safe_convert(form_data.get('price'), float, 0.00)
        stock_quantity_val = safe_convert(form_data.get('stock_quantity'), int, 0)
        
        # 2. Basic Validation
        if not name_val:
            raise ValueError("Product Name is required.")
        if price_val < 0 or stock_quantity_val < 0:
            raise ValueError("Price and Stock Quantity cannot be negative.")
            
        # 3. Create and Save Product
        new_product = Product(
            name=name_val,
            description=description_val, 
            price=price_val, 
            stock_quantity=stock_quantity_val,
            is_available=is_available_val
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        # 4. Success feedback and redirect
        flash(f"✅ Product '{new_product.name}' created successfully!")
        return redirect(url_for('create_product_form'))

    except ValueError as e:
        # Handle validation errors
        flash(f"Error: Invalid input. {e}")
        return redirect(url_for('create_product_form'))
        
    except Exception as e:
        # Handle database errors
        db.session.rollback()
        flash(f"Fatal Error: Failed to save product. Database error: {e.__class__.__name__}")
        return redirect(url_for('create_product_form'))

# --- NEW ROUTE: Product List Table ---
@app.route('/products', methods=['GET'])
def list_products_ui():
    """
    Fetches all products and renders them in an HTML table using product_list.html.
    """
    try:
        products = Product.query.all()
        product_list = [p.to_dict() for p in products]
        
        # Pass the list of dictionaries to the new template
        return render_template('product_list.html', products=product_list)
    except Exception as e:
        flash(f"Error fetching products: {e}")
        # Render an empty template with an error message
        return render_template('product_list.html', products=[])


# --- Status Route (Moved from root) ---
@app.route('/status', methods=['GET'])
def hello_world_status():
    """Returns a simple status message at the /status URL."""
    return jsonify({
        "message": "Hello World! Application is running.",
        "status": "Database connection verified during startup. API available at /api/products"
    }), 200


# --- Blueprint Registration ---
# This registers the CRUD API routes under the prefix '/api'
app.register_blueprint(product_api, url_prefix='/api')


if __name__ == '__main__':
    # Only runs the app in development mode
    app.run(debug=True)
