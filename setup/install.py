directories = ["src/Bank","src/Bank/auth","src/MBec","src/MBec/creditCard","src/MBec/usersFiles","src/Store"]

import os

everythingFine = True

for dir in directories:

    if not os.path.isdir(dir):
        everythingFine = False
        print(f" The directory {dir} is missing, we will make it for you")
        os.mkdir(dir)

if everythingFine:
    print(f" No directories missing")