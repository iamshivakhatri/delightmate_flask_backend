from flask import Flask, render_template
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Import routes
from routes import voice, agent

app.register_blueprint(voice.bp)
app.register_blueprint(agent.bp)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {"error": "Resource not found"}, 404

@app.errorhandler(500)
def server_error(error):
    return {"error": "Internal server error"}, 500

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Audio interface route
@app.route('/audio')
def audio_interface():
    return render_template('audio_recorder.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True) 