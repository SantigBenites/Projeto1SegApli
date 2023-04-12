from subprocess import *
import sys, random, os
fil = open("out.txt", "a")

randomPort = False
standartAuthFile = True

command = ["python3", "src/Bank/Bank.py"]

if randomPort:
    port = random.randrange(10000, 65535)
else:
    port = 3000

command.append("-p")
command.append(str(port))

try:

    p = run(command)

except KeyboardInterrupt:

    os.remove(f"{os.getcwd()}/src/Bank/auth/bank.auth")
    print(f"{os.getcwd()}/src/Bank/auth/bank.auth was removed")

if os.path.isfile(f"{os.getcwd()}/src/Store/bank.auth"):
    os.remove(f"{os.getcwd()}/src/Store/bank.auth")
    print(f"{os.getcwd()}/src/Store/bank.auth was removed")

if os.path.isfile(f"{os.getcwd()}/src/MBec/bank.auth was removed"):
    os.remove(f"{os.getcwd()}/src/MBec/bank.auth")
    print(f"{os.getcwd()}/src/MBec/bank.auth was removed")
    