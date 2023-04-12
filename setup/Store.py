from subprocess import *
import sys, random, os
fil = open("out.txt", "a")

randomPort = False
standartAuthFile = True

command = ["python3", "src/Store/Store.py"]

if randomPort:
    port = random.randrange(10000, 65535)
else:
    port = 5000

if standartAuthFile:

    authFile = "bank.auth"
else:
    print("Write out new authFile path")
    authFile = input()

command.append("-p")
command.append(str(port))
command.append("-s")
command.append(authFile)

try:

    p = run(command)

except KeyboardInterrupt:
    print("Store ended")