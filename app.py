# app.py

import os
import psycopg2
from flask import Flask

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