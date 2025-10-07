# app.py

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- Configuration ---
app = Flask(__name__)

# Reads the DATABASE_URL environment variable provided by Render
# This must be set in your Render Web Service settings!
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('postgresql://product_db_k4v2_user:RT2RIIydmEMUrdzAgvOsF3YNH2rwpCfr@dpg-d3ic7qje5dus7390s4gg-a/product_db_k4v2')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Minimal Entity Model: Product (Focus on one column) ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # 1. String: name (Our first data type)
    name = db.Column(db.String(100), nullable=False)
    
    # Simple representation for debugging/testing
    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

# Initial database creation (This creates the table on Render deployment)
with app.app_context():
    db.create_all()

# --- Simple Testing Route (Read/List) ---
@app.route('/api/products', methods=['GET'])
def list_products():
    # Attempt to fetch all products. If it succeeds, the database connection is good.
    try:
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products]), 200
    except Exception as e:
        # If this fails, the DATABASE_URL is likely wrong, or the DB service is down.
        return jsonify({"error": "Database connection failed or table not found.", "detail": str(e)}), 500

if __name__ == '__main__':
    # For local testing, runs on http://127.0.0.1:5000/
    # This will fail locally unless you set up a local Postgres DB.
    # We focus on the Render deployment for now.
    app.run(debug=True)