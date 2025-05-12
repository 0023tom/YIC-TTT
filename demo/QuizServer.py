from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import serial

app = Flask(__name__)
CORS(app)  # This allows cross-origin requests (required for JS fetch)

# Connect to Arduino
arduino = serial.Serial('COM4', 9600, timeout=1)

@app.route('/')
def index():
    return render_template('QuizUI.html')  # Make sure QuizUI.html is in /templates folder

@app.route('/submit', methods=['POST', 'OPTIONS'])  # Handle POST and OPTIONS
def submit():
    if request.method == 'OPTIONS':
        # Reply to CORS preflight
        return '', 200

    data = request.get_json()
    answer = data.get("answer")
    correct = data.get("correct")

    if answer == correct:
        arduino.write(b'C')
        return jsonify({"result": "Correct!"})
    else:
        arduino.write(b'W')
        return jsonify({"result": "Wrong!"})

@app.route('/nextpage')
def next_page():
    return "This is the next page after the quiz!"

if __name__ == '__main__':
    app.run(debug=False)