# app.py

from flask import Flask

# Create the Flask application instance
app = Flask(__name__)

# Define the root route ("/")
@app.route('/')
def hello_world():
    # A simple function that returns a string
    return '<h1>Labas, Diana!</h1><p>Džiaugiuosi, kad pavyko Website!.</p>'

# This block is for local testing only
if __name__ == '__main__':
    app.run(debug=True)