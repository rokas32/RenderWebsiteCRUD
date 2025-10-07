# app.py

from flask import Flask

# Create the Flask application instance
app = Flask(__name__)

# Define the root route ("/")
@app.route('/')
def hello_world():
    # A simple function that returns a string
    return '<h1>Render Product App - Setup SUCCESS!</h1><p>The web service is working correctly.</p>'

# This block is for local testing only
if __name__ == '__main__':
    app.run(debug=True)