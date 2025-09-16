#!/usr/bin/python3
# Abigail Mak
# 9/8/25
# Write a script to deliver a menu to the user such that the menu options with give them 
# 1. Display the default gateway
# 2. Test Local Connectivity
# 3. Test Remote Connectivity
# 4. Test DNS Resolution
# 5. Exit/quit the script

import os
import subprocess
import sys

def displayMenu():
    print("1. Display the Default Gateway")
    print("2. Test Local Connectivity")
    print("3. Test Remote Connectivity")
    print("4. Test DNS Resultion")
    print("Exit/quit the script")

#lets have this method dynamically retreive the default gateway
def getGateway():
    try: 
        result = subprocess.run(["ip", "r"], capture_output = True, text = True, check = True)
        for line in result.stdout.splitlines():
            if line.startswith("default"):
                return line.split()[2]
    except Exception as e:
        return f"Error finding gateway: {e}"

#lets have this method ping the gateway
def testLocal():
    gateway = getGateway()
    print(f"Pinging default gateway {gateway}...")
    subprocess.run(["ping", "-c", "4", gateway])

#lets have this one ping the remote IP address
def testRemote():
    remoteIP = "129.21.3.17"
    print(f"Pinging remote IP {remoteIP}...")
    subprocess.run(["ping", "-c", "4", remoteIP])

#lets have this one ping google
def testDNS():
    url = "www.google.com"
    print("Pinging", url, " to test DNS resolution...")
    subprocess.run(["ping", "-c", "4", url])

#lets exit the script
def exit():
    print("Exiting Script.")
    sys.exit(0)



def main():
    os.system("clear")
    while True:
        displayMenu()
        choice = input("Enter your choice by entering a number between 1 and 5: ").strip()
        if choice == "1":
            print("Default Gateway: ", getGateway())
        elif choice == "2":
            testLocal()
        elif choice == "3":
            testRemote()
        elif choice == "4":
            testDNS()
        elif choice == "5":
            exit()
        else:
            print("Invalid choice...\nPlease enter a number between 1 and 5.\n")

if __name__=="__main__":
    main()