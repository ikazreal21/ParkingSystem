from celery_app import add

result = add.delay(4, 6)
print("Task sent, waiting for result...")

# Retrieve result (blocking)
print("Result:", result.get(timeout=10))
 