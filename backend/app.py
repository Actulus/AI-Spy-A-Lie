import os
from flask import jsonify

# App Initialization
from . import create_app # from __init__ file
app = create_app(os.getenv("CONFIG_MODE"))

@app.route('/', methods=['GET'])
def hello():
    return jsonify({'msg': 'Hello from Flask!'})

if __name__ == "__main__":
    app.run()