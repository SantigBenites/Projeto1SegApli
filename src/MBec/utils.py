

def safe_execute(default, exception, function, *args):
    try:
        return function(*args)
    except exception:
        return default