import json

def safe_execute(default, exception, function, *args):
    """This function tries to use function with the *args and if it fails with exception returns default

    Args:
        default (_type_): default value if exception occurs
        exception (_type_): the exception we are checking to see if happens 
        function (_type_): function we are testing

    Returns:
        _type_: either the result of the function applied to the args or the default in case of exception
    """
    try:
        return function(*args)
    except exception:
        return default
    

def dictToJSON(dict:dict):

    JSONEncode = json.dumps(dict)

    return JSONEncode


def stringToArgs(argsString:str):

    if len(argsString > 4096):
        return 130

    sanitized = argsString.replace(" ","")
    flagBool = False
    args = []

    for char in sanitized:
        print(char)
        if flagBool:
            args[-1] += char
            flagBool = False
            args.append("")
        else:
            if char == '-':
                flagBool = True
                args.append("")
                args[-1] += char
            else:
                args[-1] += char

    return args
        


str = "-s bank.auth-u55555.user-a55555-n1000.00"

print(stringToArgs(str))