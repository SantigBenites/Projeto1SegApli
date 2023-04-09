from subprocess import *
import sys, random, os
fil = open("out.txt", "a")

command = ["python", "src/MBec/MBec.py"]

try:

    p = run(command)

except KeyboardInterrupt:
    for dir in ["src/MBec/usersFiles","src/MBec/creditCard"]:
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
            print(f"{os.path.join(dir, f)} was removed")