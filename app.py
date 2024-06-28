from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import requests
from gsHandler import retrieve_data, create_new_sheet, create_new_page, append_row, update_row
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sshtunnel import SSHTunnelForwarder
import psycopg2
import pandas as pd
import os
import plotly.graph_objects as go  # Import plotly.graph_objects
import plotly.io as pio  # Import plotly.io

def get_db_connection():
    server = SSHTunnelForwarder(
        ('letsrise.myonline.works', 22),  # SSH server and port
        ssh_username='ubuntu',  # SSH username
        ssh_pkey='~/.ssh/id_letsrise',  # Path to your private key
        remote_bind_address=('localhost', 5432)  # Database server and port
    )

    server.start()

    conn = psycopg2.connect(
        dbname='letsrise_v1',
        user='letsrise_intern',
        password='letsrise',
        host='localhost',
        port=server.local_bind_port  # Use the dynamically assigned local port
    )
    return conn, server

conn, server = get_db_connection()
query1 = """
SELECT * FROM public.user_info ui
INNER JOIN public.assessment_entries ae ON ui.user_id = ae.user_id
INNER JOIN public.consequence_results cr ON ui.user_id = cr.user_id;
"""
query2 = """
SELECT crd.*, ui.name, b.benchmark_name
FROM public.comparison_result_data crd
INNER JOIN public.user_info ui ON crd.user_id = ui.user_id
INNER JOIN public.benchmark b ON crd.benchmark_id = b.benchmark_id
ORDER BY crd.comparison_id ASC;
"""

consequence_df = pd.read_sql(query1, conn)
comparison_df = pd.read_sql(query2, conn)
conn.close()
server.stop()

consequence_df = consequence_df.loc[:, ~consequence_df.columns.duplicated()]
required_columns = ['user_id', 'name', 'email', 'age', 'linkedin_url', 'education_level', 'employment_status', 'entrepreneurial_experience', 'current_startup_stage', 'number_of_startups', 'role_in_entrepreneurship', 'industry_experience', 'number_of_previous_startups', 'location', 'gender', 'startup_name', 'assessment_id', 
                    'customer_centric', 'collaborative', 'agile', 'innovative', 'risk_taking', 'visionary', 'hustler', 'passionate', 'resilient', 'educational', 'analytical', 'frugal', 'legacy', 'digital', 'problem_solver', 
                    'delayed_product_market_fit', 'lack_of_product_market_fit', 'unable_to_complete_fundraise', 'lack_of_growth', 'lack_of_revenue', 'high_turnover_of_talent', 'inefficient_processes', 'time_consuming_client_acquisition', 'low_customer_conversion', 'low_customer_satisfaction', 'low_customer_retention', 'high_cash_burnrate', 'high_team_conflict', 'high_key_man_risk', 'lack_of_partnerships_collaborations', 'lack_of_scalability', 'lack_of_data_integrity', 'lack_of_data_security', 'lack_of_marketing', 'lack_of_motivation', 'lack_of_leadership', 'lack_of_innovation', 'lack_of_clarity', 'too_much_dependency_on_external_factors', 'lack_of_technological_advancements', 'lack_of_unique_value_proposition', 'lack_of_customer_variety', 'lack_of_intellectual_property', 'lacking_solution_quality', 'lack_of_supporters', 'missed_opportunities', 'delayed_revenue']
filtered_df = consequence_df[required_columns]

# Initialize Flask
server = Flask(__name__)
server.secret_key = 'supersecretkey'  # Secret key for session management

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

# Initialize Dash
dash_app1 = Dash(__name__, server=server, url_base_pathname='/dash1/')

# Define the trait scores and consequences
trait_scores = ['customer_centric', 'collaborative', 'agile', 'innovative', 'risk_taking', 'visionary', 'hustler', 'passionate', 'resilient', 'educational', 'analytical', 'frugal', 'legacy', 'digital', 'problem_solver']
consequences = ['delayed_product_market_fit', 'lack_of_product_market_fit', 'unable_to_complete_fundraise', 'lack_of_growth', 'lack_of_revenue', 'high_turnover_of_talent', 'inefficient_processes', 'time_consuming_client_acquisition', 'low_customer_conversion', 'low_customer_satisfaction', 'low_customer_retention', 'high_cash_burnrate', 'high_team_conflict', 'high_key_man_risk', 'lack_of_partnerships_collaborations', 'lack_of_scalability', 'lack_of_data_integrity', 'lack_of_data_security', 'lack_of_marketing', 'lack_of_motivation', 'lack_of_leadership', 'lack_of_innovation', 'lack_of_clarity', 'too_much_dependency_on_external_factors', 'lack_of_technological_advancements', 'lack_of_unique_value_proposition', 'lack_of_customer_variety', 'lack_of_intellectual_property', 'lacking_solution_quality', 'lack_of_supporters', 'missed_opportunities', 'delayed_revenue']

# Get the list of users for the dropdown
users = filtered_df[['user_id', 'name']].drop_duplicates().to_dict('records')

# Function to format consequence names
def format_consequence_name(name):
    return name.replace('_', ' ').title()

formatted_consequences = [format_consequence_name(c) for c in consequences]

# Define the layout of the app
dash_app1.layout = html.Div([
    dcc.Dropdown(
        id='user-dropdown',
        options=[{'label': user['name'], 'value': user['user_id']} for user in users],
        placeholder="Select a user",
        style={'width': '100%', 'margin': 'auto', 'font-family': 'var(--font-family)', 'color': 'var(--text-color)'}
    ),
    html.Div(id='user-info', style={'text-align': 'center', 'margin': '20px', 'font-family': 'var(--font-family)', 'color': 'var(--text-color)'}),
    html.Div([
        dcc.Graph(id='trait-scores-graph'),
        dcc.Graph(id='consequence-graph')
    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
], style={'background-color': 'var(--background-color)', 'font-family': 'var(--font-family)'})

# Define the callback to update the user info and trait scores graph based on selected user
@dash_app1.callback(
    [Output('user-info', 'children'),
     Output('trait-scores-graph', 'figure')],
    [Input('user-dropdown', 'value')]
)
def update_trait_scores(selected_user):
    if not selected_user:
        return "Please select a user to see their information.", px.bar(title="Please select a user to see their trait scores.")
    
    # Filter the data for the selected user
    user_data = filtered_df[filtered_df['user_id'] == selected_user]
    trait_data = user_data[trait_scores].melt()
    
    # Create a horizontal bar chart for the user's trait scores with increased bin sizes and no legend
    fig = px.bar(trait_data, y='variable', x='value', orientation='h', title=f'Trait Scores', 
                 labels={'variable': 'Trait', 'value': 'Score'}, color='variable', 
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(width=0.6)
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='var(--white-color)',
        paper_bgcolor='var(--background-color)',
        font=dict(family='var(--font-family)', color='var(--text-color)'),
        margin=dict(l=250, r=50, t=50, b=50),
        showlegend=False,
        yaxis_title=None,
        xaxis_title="Value"
    )

    # User info div
    user_info = html.Div([
        html.H2(user_data['name'].values[0], style={'color': 'var(--primary-color)'}),
        html.P(f"Email: {user_data['email'].values[0]}", style={'color': 'var(--text-color)'}),
        html.P(f"Age: {user_data['age'].values[0]}", style={'color': 'var(--text-color)'}),
        html.P(f"LinkedIn: {user_data['linkedin_url'].values[0]}", style={'color': 'var(--text-color)'})
    ])
    
    return user_info, fig

# Define the callback to update the consequence graph based on selected user
@dash_app1.callback(
    Output('consequence-graph', 'figure'),
    [Input('user-dropdown', 'value')]
)
def update_consequence(selected_user):
    if not selected_user:
        return px.bar(title="Please select a user to see their consequences.")
    
    # Filter the data for the selected user
    user_data = filtered_df[filtered_df['user_id'] == selected_user]
    consequence_data = user_data[consequences].melt()
    consequence_data = consequence_data[consequence_data['value'] > 0]
    
    if consequence_data.empty:
        return px.bar(title="No consequences with non-zero values for the selected user.")
    
    # Update the consequence_data variable names
    consequence_data['variable'] = consequence_data['variable'].apply(format_consequence_name)
    
    # Create a horizontal bar chart for the user's consequences with increased bin sizes and no legend
    fig = px.bar(consequence_data, y='variable', x='value', orientation='h', title=f'Consequences', 
                 labels={'variable': 'Consequence', 'value': 'Value'}, color='variable', 
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(width=0.6)
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='var(--white-color)',
        paper_bgcolor='var(--background-color)',
        font=dict(family='var(--font-family)', color='var(--text-color)'),
        margin=dict(l=250, r=50, t=50, b=50),
        showlegend=False,
        yaxis_title=None,
        xaxis_title="Value"
    )
    return fig

@server.route('/')
def index():
    session.clear()
    if 'loggedin' in session:
        return redirect(url_for('quiz'))
    return redirect(url_for('login'))

# Define the traits to be plotted
traits = ['customer_centric', 'collaborative', 'agile', 'innovative', 'risk_taking', 'visionary', 'hustler', 'passionate', 'resilient', 'educational', 'analytical', 'frugal', 'legacy', 'digital', 'problem_solver']

# Initialize the Dash app
dash_app2 = Dash(__name__, server=server, url_base_pathname='/dash2/')

# Get the list of benchmarks and users for the dropdowns
benchmarks = comparison_df['benchmark_name'].unique()
users = comparison_df[['user_id', 'name']].drop_duplicates().to_dict('records')

# Define the layout of the app
dash_app2.layout = html.Div([
    html.H1("Benchmark Comparison", style={'text-align': 'center', 'color': 'var(--primary-color)', 'font-family': 'var(--font-family)'}),
    html.Div([
        dcc.Dropdown(
            id='benchmark-dropdown',
            options=[{'label': benchmark, 'value': benchmark} for benchmark in benchmarks],
            placeholder="Select a benchmark",
            style={'width': '40%', 'display': 'inline-block', 'margin-right': '20px', 'font-family': 'var(--font-family)', 'color': 'var(--text-color)'}
        ),
        dcc.Dropdown(
            id='user-dropdown',
            options=[{'label': user['name'], 'value': user['user_id']} for user in users],
            placeholder="Select a user",
            style={'width': '40%', 'display': 'inline-block', 'font-family': 'var(--font-family)', 'color': 'var(--text-color)'}
        )
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),
    dcc.Graph(id='benchmark-graph')
], style={'background-color': 'var(--background-color)', 'font-family': 'var(--font-family)', 'padding': '20px'})

# Define the callback to update the benchmark graph based on selected benchmark and user
@dash_app2.callback(
    Output('benchmark-graph', 'figure'),
    [Input('benchmark-dropdown', 'value'), Input('user-dropdown', 'value')]
)
def update_benchmark_graph(selected_benchmark, selected_user):
    if not selected_benchmark or not selected_user:
        return px.bar(title="Please select both a benchmark and a user to see the comparison.")
    
    # Filter the data for the selected benchmark and user
    filtered_data = comparison_df[(comparison_df['benchmark_name'] == selected_benchmark) & (comparison_df['user_id'] == selected_user)]
    
    if filtered_data.empty:
        return px.bar(title="No data available for the selected benchmark and user.")
    
    # Create a vertical bar chart for the traits
    trait_data = filtered_data[traits].melt()
    fig = px.bar(trait_data, x='variable', y='value', title=f'Benchmark Comparison for {selected_benchmark}', 
                 labels={'variable': 'Trait', 'value': 'Score'}, color='variable', 
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(
        xaxis={'categoryorder':'total descending'},
        plot_bgcolor='var(--white-color)',
        paper_bgcolor='var(--background-color)',
        font=dict(family='var(--font-family)', color='var(--text-color)'),
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_title=None,
        yaxis_title="Score"
    )
    
    return fig

@server.route('/login', methods=['GET', 'POST'])
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

@server.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('login'))

@server.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@server.route('/benchmark')
def benchmark():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('benchmark.html')

@server.route('/oboarding')
def onboarding():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('onboarding.html')

@server.route('/quiz')
def quiz():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('quiz.html', questions=questions)

@server.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'loggedin' not in session:
        return jsonify({"message": "You need to log in first."}), 403

    data = request.get_json()
    answers = data.get('answers', [])

    if not answers:
        return jsonify({"message": "No answers provided."}), 400
    append_row("1yskiCZUdBlEp4PMbCVoO7981MBgSGwjnuPOLeBkieTo", "test", answers)

    return jsonify({"message": "Quiz submitted successfully!"})

@server.route('/results')
def results():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('results.html')

@server.route('/user_profile')
def profile():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('user_profile.html')

# Route to render subscriptions.html
@server.route('/subscription')
def subscription():
    if 'loggedin' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('subscription.html')  # Render subscriptions.html

if __name__ == '__main__':
    server.run(debug=True)
