import socket, sys, getopt, signal
from utils import *
from MBecModes import newAccountMode, depositMode, createCardMode, getBalanceMode, withdrawMode

global lastUsedAccount
lastUsedAccount = None

def main(args):

    try:
        while True:
            argv = input()
            if len(argv) > 4096: 
                sys.exit(130)
            argv = stringToArgs("".join(argv))
            if argv == 130:
                sys.exit(130)

            if "-n" in argv:
                messageDict = newAccountMode(argv)
            elif "-d" in argv:
                messageDict = depositMode(argv)
            elif "-c" in argv:
                messageDict = createCardMode(argv)
            elif "-g" in argv:
                messageDict = getBalanceMode(argv)
            elif "-m" in argv:
                messageDict = withdrawMode(argv)
            else:
                sys.exit(130)


            if safe_execute("error",TypeError,int,messageDict) != "error":

                return sys.exit(int(messageDict))

            print(messageDict)
    except KeyboardInterrupt:
        return sys.exit(0)
    


if __name__ == "__main__":
   main(sys.argv[1:])