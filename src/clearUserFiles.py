import os
directories = [
        #"src/Bank/users",
        "src/MBec/usersFiles",
        #"src/Bank/creditCards",
        "src/Bank/auth",
        #"src/MBec/auth"
        ]

for dir in directories:
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
        print(f"{os.path.join(dir, f)} was removed")


os.remove(f"{os.getcwd()}/src/MBec/bank.auth")
print(f"{os.getcwd()}/src/MBec/bank.auth was re removed")