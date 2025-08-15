import os
import json
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import sys

app = Flask(__name__)

# Get the absolute path to the directory containing the executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    app_dir = os.path.dirname(sys.executable)
else:
    # Running as script
    app_dir = os.path.dirname(os.path.abspath(__file__))

# Path configuration
DATA_DIR = os.path.join(app_dir, 'data')
TODOS_FILE = os.path.join(DATA_DIR, 'todos.json')
LAST_UPDATED_FILE = os.path.join(DATA_DIR, 'last_updated.txt')
TEMPLATE_FILE = os.path.join(app_dir, 'todo.html')

# Load HTML template
try:
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        HTML_TEMPLATE = f.read()
except FileNotFoundError:
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head><title>Error</title></head>
    <body>
        <h1>Template file not found!</h1>
        <p>Please make sure todo_template.html exists in the same directory.</p>
    </body>
    </html>
    """

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def check_day_change():
    """Check if day has changed and reset completed tasks if needed"""
    ensure_data_dir()
    
    today = datetime.now().date()
    last_updated = None
    
    try:
        with open(LAST_UPDATED_FILE, 'r') as f:
            last_updated_str = f.read().strip()
            last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d').date()
    except (FileNotFoundError, ValueError):
        pass
    
    if not last_updated or last_updated != today:
        # Reset completed tasks
        todos = []
        try:
            with open(TODOS_FILE, 'r') as f:
                todos = json.load(f)
                if not isinstance(todos, list):
                    todos = []
        except (FileNotFoundError, json.JSONDecodeError):
            todos = []
        
        updated_todos = []
        for todo in todos:
            if isinstance(todo, dict):
                todo['completed'] = False
                updated_todos.append(todo)
        
        with open(TODOS_FILE, 'w') as f:
            json.dump(updated_todos, f)
        
        # Update last updated date
        with open(LAST_UPDATED_FILE, 'w') as f:
            f.write(today.strftime('%Y-%m-%d'))

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/todos', methods=['GET', 'POST'])
def handle_todos():
    ensure_data_dir()
    
    if request.method == 'GET':
        try:
            with open(TODOS_FILE, 'r') as f:
                todos = json.load(f)
                return jsonify({'success': True, 'todos': todos})
        except (FileNotFoundError, json.JSONDecodeError):
            return jsonify({'success': True, 'todos': []})
    
    elif request.method == 'POST':
        todos = request.json.get('todos', [])
        with open(TODOS_FILE, 'w') as f:
            json.dump(todos, f)
        return jsonify({'success': True})

if __name__ == '__main__':
    import sys
    import webbrowser
    from threading import Timer
    
    check_day_change()
    
    # Open browser after 1 second
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000/')
    
    Timer(1, open_browser).start()
    
    # Run the application
    app.run(debug=False, port=5000)