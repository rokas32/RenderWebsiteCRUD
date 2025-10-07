
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# --- Configuration ---
app = Flask(__name__)


app.url_map.strict_slashes = False
#This ensures / works even if Render adds a trailing slash.


# When deployed on Render, it will ALWAYS use the values set in the Environment tab first.

# You must replace 'YOUR_DEFAULT_...' with the actual values you extracted from the Render Internal URL
DB_HOST = os.environ.get('DB_HOST', 'dpg-d3ic7qje5dus7390s4gg-a')
DB_NAME = os.environ.get('DB_NAME', 'product_db_k4v2')
DB_USER = os.environ.get('DB_USER', 'product_db_k4v2_user')
DB_PASS = os.environ.get('DB_PASS', 'RT2RIIydmEMUrdzAgvOsF3YNH2rwpCfr')

# --- SQLALCHEMY SETUP (Connects to DB) ---
# Construct the single connection string (URI) for Flask-SQLAlchemy
DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Configure Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the 'db' object
db = SQLAlchemy(app) 
# --- END SQLALCHEMY SETUP ---


# --- Entity Model: Product (Kept to ensure 'db' object is used) ---
class Product(db.Model):
    # This class definition is kept to ensure the 'db' object is initialized correctly
    # You can delete this later if you don't need a database at all.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # ... (rest of the columns)
    
    # We remove the to_dict method since it's no longer used

# Initial database creation (This creates/checks the table once on deploy)
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully or already exist.")
    except Exception as e:
        print(f"ERROR: Failed to create database tables. Check connection details. Error: {e}")

# ------------------------------------------------------------------
# --- SIMPLIFIED ROUTES (Replaced all CRUD and Validation) ---
# ------------------------------------------------------------------

@app.route('/', methods=['GET'])
def hello_world_status():
    """
    Returns a simple status message at the root URL (/).
    """
    return jsonify({
        "message": "Hello World! Application is running.",
        "status": "Database connection verified during startup."
    }), 200


if __name__ == '__main__':
    app.run(debug=True)