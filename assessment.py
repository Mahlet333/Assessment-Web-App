from flask import Flask, render_template_string, jsonify
import csv

app = Flask(__name__)

# Function to read questions from CSV file
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

# Load questions from CSV
questions = read_questions_from_csv('questions.csv')

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz App</title>
    <style>
        body {
            background: rgb(77, 14, 203);
            background: radial-gradient(circle, rgba(77, 14, 203, 1) 0%, rgba(255, 255, 255, 1) 100%);
            font-family: "Poppins", sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
        }

        .quiz-container {
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 0 10px 2px rgba(100, 100, 100, 0.1);
            max-width: 600px;
            width: 100%;
        }

        .quiz-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 2rem 2rem;
            box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.5);
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }

        .quiz-header h2 {
            font-size: 1.5rem;
        }

        .quiz-body {
            padding: 2rem 2rem;
        }

        .quiz-body h2 {
            padding: 1rem 0;
            font-size: 2rem;
            font-weight: 500;
            text-align: center;
            margin: 0;
        }

        .quiz-body ul {
            list-style: none;
            padding: 0;
        }

        .quiz-body ul li {
            margin: 1rem 0;
            font-size: 1rem;
            border: 1px solid #aab7b8;
            padding: 0.7rem;
            border-radius: 5px;
            cursor: pointer;
        }

        .quiz-body ul li label {
            cursor: pointer;
            padding: 0 0.4rem;
        }

        .quiz-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 2rem;
            box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.5);
        }

        .quiz-footer button {
            padding: 0.6rem 1.5rem;
            outline: none;
            background: #111;
            border: 0;
            cursor: pointer;
            font-family: inherit;
            border-radius: 5px;
            color: #fff;
            opacity: 0.9;
            transition: 0.3s ease-in-out;
        }

        .quiz-footer button:hover {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="quiz-container" id="quiz">
        <div class="quiz-header">
            <h2 class="header-txt">Assessment</h2>
        </div>
        <div class="quiz-body">
            <h2 id="question">Question Text</h2>
            <ul>
                <li>
                    <input type="radio" name="answer" id="a" class="answer" />
                    <label for="a" id="a_text">Questions</label>
                </li>
                <li>
                    <input type="radio" name="answer" id="b" class="answer" />
                    <label for="b" id="b_text">Questions</label>
                </li>
                <li>
                    <input type="radio" name="answer" id="c" class="answer" />
                    <label for="c" id="c_text">Questions</label>
                </li>
                <li>
                    <input type="radio" name="answer" id="d" class="answer" />
                    <label for="d" id="d_text">Questions</label>
                </li>
            </ul>
        </div>
        <div class="quiz-footer">
            <div class="quiz-details"></div>
            <button type="button" id="btn">Submit</button>
        </div>
    </div>
    <script>
        const quizData = """ + jsonify(questions).data.decode('utf-8') + """;

        const quiz = document.querySelector(".quiz-body");
        const answerEl = document.querySelectorAll(".answer");
        const questionEl = document.getElementById("question");
        const footerEl = document.querySelector(".quiz-footer");
        const quizDetailEl = document.querySelector(".quiz-details");
        const liEl = document.querySelector("ul li");

        const a_txt = document.getElementById("a_text");
        const b_txt = document.getElementById("b_text");
        const c_txt = document.getElementById("c_text");
        const d_txt = document.getElementById("d_text");
        const btnSubmit = document.getElementById("btn");

        let currentQuiz = 0;
        let score = 0;

        loadQuiz();

        function loadQuiz() {
            deselectAnswers();
            const currentQuizData = quizData[currentQuiz];
            questionEl.innerText = currentQuizData.question;
            a_txt.innerText = currentQuizData.options[0];
            b_txt.innerText = currentQuizData.options[1];
            c_txt.innerText = currentQuizData.options[2];
            d_txt.innerText = currentQuizData.options[3];
            quizDetailEl.innerHTML = `<p>${currentQuiz + 1} of ${quizData.length}</p>`;
        }

        // deselect
        function deselectAnswers() {
            answerEl.forEach((answerEl) => {
                answerEl.checked = false;
            });
        }

        // get selected
        function getSelected() {
            let answer;
            answerEl.forEach((answerEls) => {
                if (answerEls.checked) {
                    answer = answerEls.id;
                }
            });
            return answer;
        }

        btnSubmit.addEventListener("click", function () {
            const answers = getSelected();

            if (answers) {
                nextQuestion();
            }
        });

        // next Slide
        function nextQuestion() {
            currentQuiz++;

            if (currentQuiz < quizData.length) {
                loadQuiz();
            } else {
                quiz.innerHTML = `<h2>Thank you for completing the survey!</h2>
                <button type="button" onclick="location.reload()">Reload</button>
                `;
                footerEl.style.display = "none";
            }
        }
    </script>
</body>
</html>
""")

if __name__ == '__main__':
    app.run(debug=True)
