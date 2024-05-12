import time
from typing import Iterator


def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time

        if isinstance(result, Iterator):
            yield elapsed_time, result
        else:
            return elapsed_time, result

    return wrapper
