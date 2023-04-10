import json, re

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

    if len(argsString) > 4096:
        return 130

    sanitized = argsString.replace(" ","")
    flagBool = False
    args = []

    for char in sanitized:
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

    if len(args) != len(set(args)):
        return 130

    return args

def argsAreValidIntegers(str:str):
    return True if re.search("^[1-9]+$", str) else False
        
def argsAreValidBalances(string:str):
    validDecimal = True if re.search("^\d+\.[0-9]{0,2}$",string) else False
    validInt = False
    if validDecimal:
        validInt = 0 <= int(re.match("^\d+\.[0-9]{0,2}$",string).group(0)[:-3]) <= 4294967295
    return validDecimal and validInt

def argsAreValidFileNames(str:str):
    validSize = 1 < len(str) < 127
    validChars = True if re.search("[_\-\.0-9a-z]+\.[_\-\.0-9a-z]+",str) else False
    notDots = str != "." and str != ".."
    return validSize and validChars and notDots

def argsAreValidAccountNames(str:str):
    validSize = 1 < len(str) < 127
    validChars = True if re.search("^[0-9]+$",str) else False
    return validSize and validChars

def argsAreValidIPv4(str:str):
    validIPV4 = True if re.search("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",str) else False
    return validIPV4

def argsAreValidPort(port:int):
    return 1024 < port < 65535


def pad(s):
    BS = 16
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

def unpad(s):
    return s[:-ord(s[len(s)-1:])]