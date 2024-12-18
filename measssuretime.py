import time

def timeit():
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            func(*args, **kwargs)
            end = time.time()
            print(f"running time: {end - start} secs")
            return end - start
        return wrapper
    return decorator
