from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/hello', methods=['GET'])
def get_hello():
    return jsonify({'msg': 'Hello from Flask!'})

if __name__ == '__main__':
    app.run(debug=True)