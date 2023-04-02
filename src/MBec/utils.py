import json

def safe_execute(default, exception, function, *args):
    try:
        return function(*args)
    except exception:
        return default
    

def dictToJSON(dict:dict):

    JSONEncode = json.dumps(dict)

    return JSONEncode