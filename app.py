# app.py

import os
# Check this line carefully!
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- Configuration ---
app = Flask(__name__)
# Allows both / and /api/products/ to work without strict trailing slashes
app.url_map.strict_slashes = False 

# Database credentials (These read from Render Environment Variables when deployed)
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

# NOTE: db.create_all() is now called manually via the Flask CLI command defined in cli.py


# --- Blueprint Registration ---
# This registers the CRUD routes under the prefix '/api'
app.register_blueprint(product_api, url_prefix='/api')




# --- Root Status Check Route ---
# --- Root Status Check Route (Keep this one!) ---
@app.route('/', methods=['GET'])
def hello_world_status():
    """Returns a simple status message at the root URL (/) to confirm the app is running."""
    return jsonify({
        "message": "Hello World! Application is running.",
        "status": "Database connection verified during startup. API available at /api/products"
    }), 200

# --------------------------------------------------------------------------------------

# --- Frontend Form Route (Add this one!) ---
@app.route('/create', methods=['GET'])
def create_product_form():
    """Renders the HTML form for inputting new product data."""
    # Ensure 'create_product.html' is spelled exactly right
    return render_template('create_product.html')

# Don't forget the companion POST route for submission:
@app.route('/create-submit', methods=['POST'])
def submit_product():
    # ... (form processing logic goes here) ...
    pass




if __name__ == '__main__':
    app.run(debug=True)