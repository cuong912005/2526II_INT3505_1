from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

users = [
    {"id": 1, "name": "Nguyen Van A"},
    {"id": 2, "name": "Tran Thi B"}
]

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/users')
def get_users():
    return jsonify(users), 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
