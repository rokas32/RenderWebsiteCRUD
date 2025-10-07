# app.py

import os
import psycopg2
from flask import Flask

# --- Configuration ---
app = Flask(__name__)

# Reads the DATABASE_URL environment variable provided by Render
DATABASE_URL = os.environ.get('postgresql://product_db_k4v2_user:RT2RIIydmEMUrdzAgvOsF3YNH2rwpCfr@dpg-d3ic7qje5dus7390s4gg-a/product_db_k4v2')

# --- Connection Test Route ---
@app.route('/')
def connection_test():
    if not DATABASE_URL:
        # This means the environment variable wasn't set on Render
        return '<h1>Connection Test FAILED</h1><p>Error: DATABASE_URL environment variable is missing on Render.</p>', 500
    
    conn = None
    try:
        # Attempt to establish a connection using the URL
        conn = psycopg2.connect(DATABASE_URL)
        
        # If the line above executes without error, the connection is good.
        conn.close() 
        
        return '<h1>Connection Test SUCCESS! 🎉</h1><p>Flask is running AND successfully connected to the PostgreSQL database.</p>'
        
    except Exception as e:
        # If any error occurs during the connection attempt
        return f'<h1>Connection Test FAILED! ❌</h1><p>Flask is running, but could not connect to PostgreSQL.</p><p>Detail: {e}</p>', 500
    
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    # For local testing only
    app.run(debug=True)