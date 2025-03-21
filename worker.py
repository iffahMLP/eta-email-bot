import os
import redis
import rq
from app import process_orders

# Connect to Redis
REDIS_URL = os.getenv("REDIS_URL")
redis_conn = redis.from_url(REDIS_URL)
queue = rq.Queue('order_queue', connection=redis_conn)

if __name__ == "__main__":
    worker = rq.Worker([queue], connection=redis_conn)
    worker.work()
