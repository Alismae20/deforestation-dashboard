"""
Frontend Flask server - serves the deforestation dashboard.
"""

from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('index.html')


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files."""
    return send_from_directory('static/css', filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files."""
    return send_from_directory('static/js', filename)


if __name__ == '__main__':
    print("Starting Deforestation Dashboard Frontend...")
    app.run(debug=True, host='127.0.0.1', port=8000)
