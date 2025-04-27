from flask import Flask, render_template, session, request
from dotenv import load_dotenv
import os
from app.extensions import redis_client
import json

from app.utils.supabase import get_supabase_client
import uuid
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)







# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Set a secret key for session management
app.secret_key = os.environ.get('SECRET_KEY')

# Import routes
from app.routes.voice import bp as voice_bp
from app.routes.agent import bp as agent_bp
from app.routes.email import email_bp


app.register_blueprint(voice_bp)
app.register_blueprint(agent_bp)
app.register_blueprint(email_bp)

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
    supabase = get_supabase_client()
    
    return render_template('index.html')

# Audio interface route
@app.route('/audio')
def audio_interface():
    return render_template('audio_recorder.html')




@app.route('/view_jobs')
def view_jobs():
    # Get pending jobs
    pending = redis_client.lrange('email_jobs', 0, -1)
    pending_jobs = [json.loads(job) for job in pending]

    # Get completed jobs
    completed = redis_client.lrange('completed_jobs', 0, -1)
    completed_jobs = [json.loads(job) for job in completed]

    return render_template('view_jobs.html', pending_jobs=pending_jobs, completed_jobs=completed_jobs)


@app.route('/job_queue_ui')
def job_queue_ui():
    return render_template('job_queue.html')


@app.route('/enqueue_job', methods=['POST'])
def enqueue_job():
    job_type = request.form.get('job_type', 'summarize')
    email_content = request.form.get('email_content', 'default email content')

    job = {
        "type": job_type,
        "content": email_content
    }

    redis_client.lpush('email_jobs', json.dumps(job))

    return {"message": "Job enqueued successfully!"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True) 