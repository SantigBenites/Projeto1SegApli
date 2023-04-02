from subprocess import *
import sys
fil = open("out.txt", "a")
#call(["python", "src/Bank/Bank.py"])

#call(["python", "src/Store/Store.py"])

call(["python", "src/MBec/MBec.py","-u" ,"55555.user", "-a", "55555", "-n" ,"1000.00"], stdout= fil)

#-s bank.auth -u 55555.user -a 55555 -d 100.00
call(["python", "src/MBec/MBec.py","-u", "55555.user" ,"-a" ,"55555" ,"-d" ,"100.00"], stdout=fil)

#-s bank.auth -u 55555.user -a 55555 -c 63.10
call(["python", "src/MBec/MBec.py","-u", "55555.user" ,"-a" ,"55555" ,"-c" ,"63.10"], stdout=fil)

#-s 55555_2.card -m 45.10
call(["python", "src/MBec/MBec.py","-s", "55555_2.card" ,"-m" ,"45.10"], stdout=fil)


#-s bank.auth -u 55555.user -a 55555 -c 2000.00
call(["python", "src/MBec/MBec.py","-u", "55555.user" ,"-a" ,"55555" ,"-c" ,"2000.00"], stdout=fil)

#-s bank.auth -u 55555.user -a 55555 -c 150.00
call(["python", "src/MBec/MBec.py","-u", "55555.user" ,"-a" ,"55555" ,"-c" ,"150.00"], stdout=fil)

#-s 55555_2.card -m 70.00
call(["python", "src/MBec/MBec.py","-s", "55555_2.card" ,"-m" ,"70.00"], stdout=fil)

#-u 55555 -n 2000.00
call(["python", "src/MBec/MBec.py","-u" ,"55555.user", "-n" ,"2000.00"], stdout= fil)

#-s bank.auth -u 66666.user -a 66666 -n 1500.00
call(["python", "src/MBec/MBec.py","-u", "6666.user" ,"-a" ,"6666" ,"-n" ,"1500.00"], stdout=fil)

# -a 66666 -c 55555.card -g
call(["python", "src/MBec/MBec.py","-a" ,"6666" ,"-c" ,"5555.card", "-g"], stdout=fil)

