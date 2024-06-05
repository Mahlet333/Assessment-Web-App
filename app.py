from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import csv
import json
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Secret key for session management

# Dummy credentials
DUMMY_EMAIL = 'letsrisewebapp@gmail.com'
DUMMY_PASSWORD = 'letsrise1234'

def read_questions_from_csv(file_path):
    questions = []
    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            questions.append({
                "question": row['question'],
                "options": [row['option1'], row['option2'], row['option3'], row['option4']]
            })
    return questions

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
            return redirect(url_for('user_info'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/user_info', methods=['GET', 'POST'])
def user_info():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        industry = request.form['industry']

        # Store user info in session
        session['user_info'] = {
            'name': name,
            'email': email,
            'industry': industry
        }

        return redirect(url_for('quiz'))

    return render_template('user_info.html')

@app.route('/quiz')
def quiz():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if 'user_info' not in session:
        return redirect(url_for('user_info'))

    return render_template('quiz.html', questions=questions)

# Function to send data to Google Sheets
def send_data_to_google_sheets(name, email, industry):
    url = 'https://script.google.com/a/macros/nyu.edu/s/AKfycbxnZ5aNtf_9QZqF-gdTTmNkMRmpCAWiQxOrb9pzw3YDHQMRJbqQJm8Q4z9fygUZbXQ/exec'
    data = {
        'name': name,
        'email': email,
        'industry': industry
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Data sent successfully to Google Sheets!")
    else:
        print("Failed to send data to Google Sheets.")

@app.route('/submit_form', methods=['POST'])
def submit_form():
    name = request.form['name']
    email = request.form['email']
    industry = request.form['industry']
    send_data_to_google_sheets(name, email, industry)
    return "Form submitted successfully!"

if __name__ == '__main__':
    app.run(debug=True)
