import os
directories = ["src/Bank/users",
        "src/MBec/usersFiles"]

for dir in directories:
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
        print(f"{os.path.join(dir, f)} was removed")