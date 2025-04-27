import redis

# Build the connection URL first
REDIS_URL = "redis://default:zLGGlwmbYWg2YTiC0ighWpEwVqZtNCdc@redis-17241.c11.us-east-1-3.ec2.redns.redis-cloud.com:17241"


# Create a Redis client using the URL
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True  # decode bytes to str automatically
)

# # Example usage
# redis_client.set("foo", "bar")
# result = redis_client.get("foo")
# print(result)  # >>> bar
