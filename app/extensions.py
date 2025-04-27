import redis
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build the connection URL first
REDIS_URL = os.environ.get("REDIS_URL")

# Create a Redis client using the URL
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True  # decode bytes to str automatically
)

# # Example usage
# redis_client.set("foo", "bar")
# result = redis_client.get("foo")
# print(result)  # >>> bar
