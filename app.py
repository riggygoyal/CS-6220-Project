# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return "Welcome to the Course Schedule Generator!"


@app.route('/generate_schedule', methods=['GET', 'POST'])
def generate_schedule():
    if request.method == 'POST':
        data = request.json
        print("Received POST request with data:", data)
    else:
        print("Received a GET request")

    return {"status": "Received"}


if __name__ == '__main__':
    app.run(debug=True)
