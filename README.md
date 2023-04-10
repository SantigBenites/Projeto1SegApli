# Projeto1SegApli

TP21-G04 

Santiago Benites
Inês Martins 
Miguel Carvalho 

https://github.com/SantigBenites/Projeto1SegApli

Project done with python

# TODO

- Add more needed verifications like time part of message DH 
- testing 


# Git commands

## Starting the repo
```
echo "# Projeto1SegApli" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:SantigBenites/Projeto1SegApli.git
git push -u origin main
```

## Commiting to repo

```
git pull origin main (careful with pulling over non committed work)
git add -A
git commit -m "message"
git push origin main
```

# Instalation

## Python

In order to install our program we will require the python programming language, taking this into account we recommend at least python version 3.10 which was the one we were using

First run ``` python -V``` this will check if you already have python installed
If you don't just follow one of the tutorials online, but take into account we will require python with version 3.10 or above. 

Moreover we recommend the usage of a package manager like conda or mamba, if any are installed it can simplify the process.

But it is not required in our tutorial, if you do have a package manager installed you can just follow the tutorial we will give little warning wherever your path might deviate from the normal installation

## Required packages

The installation will require some packages, these can be found in the setup folder under the requirements.txt

In another note if you prefer it can be simpler to just run the pip install commands from you current python installation

The commands would be

```
pip install pycryptodome
pip install cryptography
```

If you are using an alternative package manager the best help I can give is to try to replace pip with your package manager, be it mamba/conda/other...

# Running the program

You probably received a specific file structure, please don't disturb it, as it is required from normal execution.
In order to run either MBec or the Store the bank.auth file is required to be present in the root directory of both of these (take account that bank,auth is just the standard name of the file, it can change if you want to). 

This means that bank.auth needs to be present in both src/MBec and src/Store so that the store and the MBec can run, if this is not true they will not  start and both the program will instantly exit.

To run programs the required commands are

```
python3 src/Bank/Bank.py [-p <bk-port>] [-s <auth-file>]

python3 src/MBec/MBec.py

python3 src/Store/Store.py [-p <st-port>] [-s <auth-file>]
```

When the required programs are run, MBec will now be able to take in input from the stdin. 
The input should be in the forms present in the project description

```
mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -n <balance>
mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -d <amount>
mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -c <amount>
mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -g
mbec [-i <ip-store-address>] [-p <st-port>] [-v <virtual-credit-card-file>] -m <shopping-value>
```

In these declarations, the order of the input doesn't matter, nor does if the input has spaces between them.

Therefore the following commands do the same thing
```
python3 src/MBec/MBec.py
-a5000-n123.00

python3 src/MBec/MBec.py
-a 5000 -n 123.00
```
Take into account that all values should follow the project's directives, therefore a monetary value should be presented with its decimals, separated by a dot, if 123.00 were to be exchanged with 123, the program would not accept it.

Command will be taken from the stdin, and cannot exceed 4096 characters