

def safe_execute(default, exception, function, *args):
    try:
        return function(*args)
    except exception:
        return default
    

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

    return args

def pad(s):
    BS = 16
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

def unpad(s):
    return s[:-ord(s[len(s)-1:])]