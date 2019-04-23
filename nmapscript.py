s = open("nmapoutput.txt", "r")
count = 0

line_iter = iter(s)

for line in line_iter:
    count += 1
    flag = True
    if "Nmap scan report for " in line:
        arr = line.split()
        print(arr[-1])

    if "Host is up " not in line and len(line) != 1 and "Not shown" not in line and "Nmap" not in line and "Service" not in line:
        print(line)
  
"""     
    if "PORT" in line:
        while(line != '\n'):
            print(line)
            next(line_iter)
        

    if flag==True:
       if "Nmap scan report for " in line:
           flag = False
       else:
           print(line)
"""

if count == 2:
    print("No hosts found.")

