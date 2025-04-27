from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
from extensions import redis_client
import json





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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True) 