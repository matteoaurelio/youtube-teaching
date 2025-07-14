from flask import Flask, request, render_template_string, redirect, url_for
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

# --- Database Functions ---

def get_db_connection():
    """Establishes a connection to the database."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
    return connection

def get_all_goals():
    """Fetches all goals from the database."""
    connection = get_db_connection()
    if connection is None or not connection.is_connected():
        return []

    goals = []
    try:
        cursor = connection.cursor()
        # Create table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS goals (
                           id INT AUTO_INCREMENT PRIMARY KEY,
                           task VARCHAR(255) NOT NULL)
                           ''')
        
        cursor.execute("SELECT task FROM goals")
        rows = cursor.fetchall()
        goals = [row[0] for row in rows] # Extract task string from each tuple
    except Error as e:
        print(f"Error fetching goals: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return goals

def add_goal(task):
    """Adds a new goal to the database."""
    connection = get_db_connection()
    if connection is None or not connection.is_connected():
        return

    try:
        cursor = connection.cursor()
        insert_query = "INSERT INTO goals (task) VALUES (%s)"
        cursor.execute(insert_query, (task,))
        connection.commit()
    except Error as e:
        print(f"Error adding goal: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    # If the user is submitting a new goal
    if request.method == 'POST':
        new_goal = request.form['task']
        if new_goal: # Make sure it's not empty
            add_goal(new_goal)
        return redirect(url_for('index'))

    # If the user is just viewing the page, display all goals
    current_goals = get_all_goals()
    
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Today's Goals</title>
        <style>
            body { font-family: sans-serif; margin: 2em; }
            li { margin-bottom: 0.5em; }
        </style>
    </head>
    <body>
        <h1>Today's Goals ✅</h1>
        <form method="POST">
            New Goal: <input type="text" name="task" size="40">
            <input type="submit" value="Add Goal">
        </form>
        <hr>
        <h2>Current Goals:</h2>
        <ul>
            {% for goal in goals %}
                <li>{{ goal }}</li>
            {% endfor %}
        </ul>
    </body>
    </html>
    '''
    return render_template_string(html_template, goals=current_goals)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)