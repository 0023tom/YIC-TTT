from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import serial
import subprocess

app = Flask(__name__)
CORS(app)  # This allows cross-origin requests (required for JS fetch)

# Connect to Arduino
arduino = serial.Serial('COM4', 9600, timeout=1)

def get_deepseek_question():
    prompt = "Generate a multiple choice question for a quiz, including options and the correct answer."

    try:
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1:1.5b", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
        )

        if result.returncode != 0:
            return {"error": "Error generating question: " + result.stderr}

        response = result.stdout.strip()
        print(f"Received response: {response}")

        # Extract only the part after </think>
        if "</think>" in response:
            response = response.split("</think>")[-1].strip()

        print(f"Parsed content: {response}")

        # Now extract structured data
        question = ""
        options = []
        correct_answer = ""
        explanation = ""

       # Strip and clean markdown and empty entries
        def clean_lines(raw):
            return [line.strip("* ").strip() for line in raw.splitlines() if line.strip()]

        if "Question:" in response:
            question = response.split("Question:")[1].split("Options:")[0].strip()
            question = question.strip("* ").strip()
            print(f"Question: {question}")

        if "Options:" in response:
            raw_options = response.split("Options:")[1].split("Correct Answer:")[0].strip()
            options = clean_lines(raw_options)
            print(f"Options: {options}")

        if "Correct Answer:" in response:
            correct_answer = response.split("Correct Answer:")[1].split("Explanation:")[0].strip()
            correct_answer = correct_answer.strip("* ").strip()
            print(f"Answer: {correct_answer}")

        if "Explanation:" in response:
            explanation = response.split("Explanation:")[1].strip()

        print(f"Parsed response: Question: {question}, Options: {options}, Correct Answer: {correct_answer}, Explanation: {explanation}")

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation
        }

    except Exception as e:
        print(f"Error processing response: {str(e)}")
        return {"error": f"Error processing response: {str(e)}"}

@app.route('/')
def index():
    return render_template('test.html')  # Ensure this file exists in /templates

@app.route('/question')
def get_question():
    question_data = get_deepseek_question()
    
    if "error" in question_data:
        return jsonify({"error": question_data["error"]}), 500
    
    return jsonify(question_data)

@app.route('/submit', methods=['POST', 'OPTIONS'])
def submit():
    if request.method == 'OPTIONS':
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

if __name__ == '__main__':
    app.run(debug=False)
