import socket, sys, getopt, signal
from utils import safe_execute
from MBecModes import newAccountMode, depositMode, createCardMode, getBalanceMode, withrawMode

def main(argv:list[str]):

    print(f"argv is {argv}")
    if "-n" in argv:
        messageDict = newAccountMode(argv)
    elif "-d" in argv:
        messageDict = depositMode(argv)
    elif "-c" in argv:
        messageDict = createCardMode(argv)
    elif "g" in argv:
        messageDict = getBalanceMode(argv)
    elif "-m"in argv:
        messageDict = withrawMode(argv)
    else:
        sys.exit(1)
    


if __name__ == "__main__":
   main(sys.argv[1:])