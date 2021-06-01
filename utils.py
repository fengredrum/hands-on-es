import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print('Time spends: {:.2f} s'.format(time.time() - start))
        return res

    return wrapper
