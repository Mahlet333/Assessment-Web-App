from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import csv
import json
import requests
from gsHandler import retrieve_data, create_new_sheet, create_new_page, append_row, update_row

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Secret key for session management

# Dummy credentials
DUMMY_EMAIL = 'letsrisewebapp@gmail.com'
DUMMY_PASSWORD = 'letsrise1234'

def read_questions_from_json(file_path):
    with open(file_path, mode='r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    
    questions = []
    for key, value in data.items():
        question = {
            "question": f"Question {key}",
            "options": [item["Decision Statement"] for item in value]
        }
        questions.append(question)   
    return questions

# Load questions from JSON
questions = read_questions_from_json('assessment_google_sheet.json')

@app.route('/')
def index():
    session.clear()
    if 'loggedin' in session:
        return redirect(url_for('quiz'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == DUMMY_EMAIL and password == DUMMY_PASSWORD:
            session['loggedin'] = True
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/oboarding')
def onboarding():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('onboarding.html')

@app.route('/quiz')
def quiz():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('quiz.html', questions=questions)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'loggedin' not in session:
        return jsonify({"message": "You need to log in first."}), 403

    data = request.get_json()
    answers = data.get('answers', [])

    if not answers:
        return jsonify({"message": "No answers provided."}), 400
    append_row("1yskiCZUdBlEp4PMbCVoO7981MBgSGwjnuPOLeBkieTo", "test", answers)

    return jsonify({"message": "Quiz submitted successfully!"})

@app.route('/results')
def results():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)
