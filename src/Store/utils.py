import re

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
    
    if sanitized == "":
        return args

    if sanitized[0] != "-":
        return 130

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

    if len(args) != len(set(args)):
        return 130

    return args

def argsAreValidIntegers(str:str):
    return True if re.search("^[1-9]+$", str) else False
        
def argsAreValidBalances(string:str):
    validDecimal = True if re.search("^\d+\.[0-9]{0,2}$",string) else False
    validInt = False
    if validDecimal:
        validInt = 0 < int(re.match("^\d+\.[0-9]{0,2}$",string).group(0)[:-3]) < 4294967295
    return validDecimal and validInt

def argsAreValidFileNames(str:str):
    validSize = 1 < len(str) < 127
    validChars = True if re.search("[\_\-\.0-9a-z]+",str) else False
    notDots = str != "." and str != ".."
    singleMatch = len(re.findall("[\_\-\.0-9a-z]+",str)) == 1
    return validSize and validChars and notDots and singleMatch

def argsAreValidAccountNames(str:str):
    validSize = 1 < len(str) < 127
    validChars = True if re.search("^[0-9]+$",str) else False
    return validSize and validChars

def argsAreValidIPv4(str:str):
    validIPV4 = True if re.search("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",str) else False
    return validIPV4

def argsAreValidPort(port:int):
    return 1024 < port < 65535