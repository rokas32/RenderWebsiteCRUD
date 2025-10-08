import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import the Blueprint containing the CRUD API routes
from product_routes import product_api

# --- Configuration ---
app = Flask(__name__)
# Set a secret key for session management (required for flash messages)
app.config['SECRET_KEY'] = os.environ.get('SECRET_SECRET_KEY', 'a_secret_key_for_flash')
app.url_map.strict_slashes = False 

# Database credentials (These must match your current Render PostgreSQL credentials)
DB_HOST = os.environ.get('DB_HOST', 'dpg-d3ic7qje5dus7390s4gg-a')
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
        raise ValueError(f"Input '{value}' must be a valid number of type {target_type.__name__}.")


# --- Frontend Routes (Form Display and Submission) ---

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
        
        # 4. Success feedback and redirect to the product list (Redirect to /products)
        flash(f"✅ Product '{new_product.name}' created successfully!")
        return redirect(url_for('list_products_ui'))

    except ValueError as e:
        # Handle validation errors (e.g., name missing, non-numeric input)
        flash(f"Error: Invalid input. {e}")
        return redirect(url_for('create_product_form'))
        
    except Exception as e:
        # Handle database errors (e.g., connection lost, type issue)
        db.session.rollback()
        flash(f"Fatal Error: Failed to save product. Database error: {e.__class__.__name__}. Check your DB credentials!")
        return redirect(url_for('create_product_form'))

# --- NEW ROUTE: Product List Table (Read UI) ---
@app.route('/products', methods=['GET'])
def list_products_ui():
    """Fetches all products and renders them in an HTML table."""
    try:
        products = Product.query.all()
        # Convert models to dictionaries for rendering in Jinja2
        product_list = [p.to_dict() for p in products]
        
        return render_template('product_list.html', products=product_list)
    except Exception as e:
        flash(f"Error fetching products: {e}")
        return render_template('product_list.html', products=[])

# --- NEW ROUTE: Delete Product (Delete UI) ---
@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product_ui(product_id):
    """Handles the form submission for deleting a product."""
    product = Product.query.get_or_404(product_id)
    product_name = product.name
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash(f"🗑️ Product '{product_name}' (ID: {product_id}) successfully deleted.")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error deleting product: {e}")

    return redirect(url_for('list_products_ui'))

# app.py additions

# --- NEW ROUTE: Display Edit Product Form (Update UI - GET) ---
@app.route('/edit/<int:product_id>', methods=['GET'])
def edit_product_form(product_id):
    """Fetches a specific product and renders the edit form."""
    # Retrieve the product or show a 404 error if not found
    product = Product.query.get_or_404(product_id)
    # Pass the product object (which can be accessed in Jinja2) to the template
    return render_template('edit_product.html', product=product)


# --- NEW ROUTE: Submit Product Edits (Update UI - POST) ---
@app.route('/edit/<int:product_id>', methods=['POST'])
def update_product_ui(product_id):
    """Handles the form submission for updating an existing product."""
    product = Product.query.get_or_404(product_id)
    form_data = request.form
    
    try:
        # 1. Input Cleaning and Conversion (Re-using logic from submit_product)
        name_val = form_data.get('name', '').strip()
        description_val = form_data.get('description', '').strip()
        price_val = safe_convert(form_data.get('price'), float, 0.00)
        stock_quantity_val = safe_convert(form_data.get('stock_quantity'), int, 0)
        # Checkbox is 'on' if checked, or None if unchecked.
        is_available_val = True if form_data.get('is_available') == 'on' else False
        
        # 2. Basic Validation
        if not name_val:
            raise ValueError("Product Name is required.")
        if price_val < 0 or stock_quantity_val < 0:
            raise ValueError("Price and Stock Quantity cannot be negative.")

        # 3. Update Product Fields
        product.name = name_val
        product.description = description_val
        product.price = price_val
        product.stock_quantity = stock_quantity_val
        product.is_available = is_available_val
        
        db.session.commit()
        
        # 4. Success feedback and redirect to the product list
        flash(f"🎉 Product '{product.name}' (ID: {product_id}) updated successfully!")
        return redirect(url_for('list_products_ui'))

    except ValueError as e:
        db.session.rollback()
        # Pass the original product back to the template to pre-fill the form with failed submission data
        flash(f"Error: Invalid input. {e}")
        # Use redirect to GET edit page so flash message is shown and form fields are empty/reset
        # A more robust solution would be to render_template directly here and pass the form_data back
        return redirect(url_for('edit_product_form', product_id=product_id))

    except Exception as e:
        db.session.rollback()
        flash(f"Fatal Error: Failed to update product. Database error: {e.__class__.__name__}.")
        return redirect(url_for('edit_product_form', product_id=product_id))


# --- Status Route ---
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
    with app.app_context():
        db.create_all()
    app.run(debug=True)
