"""
Test script to create multiple simultaneous database connections
This will trigger the MaxClientsInSessionMode error with Session Pooler
"""
from database import engine
from sqlalchemy import text
import threading
import time

def test_connection(thread_id):
    """Each thread opens a connection and holds it for a bit"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"Thread {thread_id}: Connection successful!")
            time.sleep(5)  # Hold the connection for 5 seconds
    except Exception as e:
        print(f"Thread {thread_id}: ERROR - {e}")

# Create 20 threads that will try to connect simultaneously
threads = []
print("Starting 20 simultaneous connection attempts...")
for i in range(20):
    t = threading.Thread(target=test_connection, args=(i,))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

print("All threads completed!")
