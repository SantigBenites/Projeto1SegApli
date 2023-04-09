import socket, sys, getopt, signal
from utils import *
from MBecModes import newAccountMode, depositMode, createCardMode, getBalanceMode, withdrawMode

def main(args):

    try:
        while True:
            argv = input()
            if len(argv) > 4096: 
                return
            argv = stringToArgs("".join(argv))
            print(argv)

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
                sys.exit(1)


            if safe_execute("error",TypeError,int,messageDict) != "error":

                return int(messageDict)

            print(messageDict)
    except KeyboardInterrupt:
        return 0
    


if __name__ == "__main__":
   main(sys.argv[1:])