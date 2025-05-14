import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration_ms = round((time.time() - start) * 1000, 2)
        print(f"{func.__name__} executed in {duration_ms} ms")
        return result
    return wrapper