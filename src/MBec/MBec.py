import socket, sys, getopt, signal
from utils import *
from MBecModes import newAccountMode, depositMode, createCardMode, getBalanceMode, withdrawMode

def main(argv:list[str]):

    print(f"argv is {argv}")
    if "-n" in argv:
        messageDict = newAccountMode(argv)
    elif "-d" in argv:
        messageDict = depositMode(argv)
    elif "-c" in argv:
        messageDict = createCardMode(argv)
    elif "-g" in argv:
        messageDict = getBalanceMode(argv)
    elif "-m"in argv:
        messageDict = withdrawMode(argv)
    else:
        sys.exit(1)

    if safe_execute(0,TypeError,int,argv[argv.index("-c")+1]) == 0:
        
        return int(messageDict)

    print(messageDict)
    return 0
    


if __name__ == "__main__":
   main(sys.argv[1:])