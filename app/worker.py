
import json
import time
from extensions import redis_client


def simulate_summarization(email_content):
    time.sleep(20)
    return f"Summary of: {email_content[:20]}..."

def simulate_drafting(email_content):
    time.sleep(20)
    return f"Draft reply to: {email_content[:20]}..."

def worker():
    print("Worker started, waiting for jobs...")
    while True:
        job_data = redis_client.brpop('email_jobs', timeout=0)
        queue_name, job_json = job_data
        job = json.loads(job_json)

        if job['type'] == 'summarize':
            result = simulate_summarization(job['content'])
        elif job['type'] == 'draft':
            result = simulate_drafting(job['content'])
        else:
            result = f"Unknown job type: {job['type']}"

        # Save result into a completed list
        completed_job = {
            "original_job": job,
            "result": result
        }
        redis_client.lpush('completed_jobs', json.dumps(completed_job))
        redis_client.ltrim('completed_jobs', 0, 9)  # Keep only the last 10 jobs

        print(f"Processed Job: {job} -> {result}")

if __name__ == "__main__":
    worker()
