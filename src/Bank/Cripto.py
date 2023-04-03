
import hashlib


def hashFile(filePath:str):
    file  = open(filePath, "r")
    c = file.read()
    file.close()
    return hashlib.sha256(c.encode()).hexdigest()
    
    