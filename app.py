from flask import Flask, request, jsonify
import psycopg2
import os
import json
import rq
import redis
from google_sheet_handler import GoogleSheetHandler

app = Flask(__name__)

# Connect to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Connect to Redis for background jobs
REDIS_URL = os.getenv("REDIS_URL")
redis_conn = redis.from_url(REDIS_URL)
queue = rq.Queue('order_queue', connection=redis_conn)

# Initialize Google Sheets Handler
sheet_handler = GoogleSheetHandler()

# Initialize PostgreSQL Table
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temp_orders (
            order_number TEXT PRIMARY KEY,
            order_data TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/shopify/order', methods=['POST'])
def shopify_order_webhook():
    """Receives order data from Shopify Flow and saves it to PostgreSQL."""
    order_data = request.json
    order_number = order_data.get("order_number")

    if not order_number:
        return jsonify({"error": "Invalid order data"}), 400

    # Store order in PostgreSQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO temp_orders (order_number, order_data) VALUES (%s, %s) ON CONFLICT DO NOTHING", 
                   (order_number, json.dumps(order_data)))
    conn.commit()
    conn.close()

    # Queue background job to process order
    queue.enqueue(process_orders)

    return jsonify({"message": "Order received and stored temporarily", "order_number": order_number}), 200

def process_orders():
    """Check temp storage and write missing orders to Google Sheets."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT order_number, order_data FROM temp_orders")
    orders = cursor.fetchall()

    for order_number, order_data in orders:
        order_data = json.loads(order_data)  # Convert string back to dictionary
        if sheet_handler.write_order(order_data):
            cursor.execute("DELETE FROM temp_orders WHERE order_number = %s", (order_number,))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
