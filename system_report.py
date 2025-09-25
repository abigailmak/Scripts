#!/usr/bin/python3
#Abigail Mak
#9/23/2025
#Write a script to generate a system report and prints it to the terminal.

import os
import platform
import socket
import subprocess
from datetime import datetime
from ipaddress import IPv4Interface

def run(cmd: str) -> str:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip();

#lets collect all the info
def getDomainSuf():
    #First try the hostname command
    domain = run("hostname -d")
    if domain:
            return domain
    #if that fails, peek at resolv.conf
    return run("grep -m1 'search' /etc/resolv.conf | awk '{print $2}'") or "N/A"


def getIPandMask():
    #find the primary IPv4 address and convert its mask into dotted form
    line = run("ip -o -4 addr show scope global | head -1")
    if not line:
        return "N/A", "N/A"
    parts = line.split()
    cidr = parts[3] #should look like 192.168.1.10/24
    iface = IPv4Interface(cidr)
    return str(iface.ip), str(iface.netmask)

def getGateway():
    return run("ip route | awk '/^default/ {print $3}'") or "N/A"

def getDNSservers():
    #Grab the first two DNS servers from resolv.conf
    servers = run("grep '^nameserver' /etc/resolv.conf | awk '{print $2}'").splitlines()
    return servers[0] if len(servers)>0 else "N/A", servers[1] if len(servers)>1 else "N/A"

def getOSInfo():
    #Get OS name, version, and kernel
    osName = run("grep -m1 '^PRETTY_NAME=' /etc/*release | cut -d= -f2 | tr -d '\"'") or platform.system()
    version = run("grep -m1 'VERSION_ID=' /etc/*release | cut -d= -f2 |tr -d '\"'") or "N/A"
    kernel = platform.release()
    return osName, version, kernel

def getDiskInfo():
    #Return the total availabile safe on the root filesystem
    line = run("df -h / | tail -1")
    parts = line.split()
    return parts[1] if len(parts) > 1 else "N/A", parts[3] if len(parts) > 3 else "N/A"

def getCPUInfo():
    #Return CPU model, num of CPUs, and num of cores
    model = run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2-").strip() or "N/A"
    cpuCount = len(set(run("grep 'physical id' /proc/cpuinfo | awk '{print $4}'").split())) or 1
    coreCount = sum(int(x) for x in run("grep 'cpu cores' /proc/cpuinfo | awk -F: '{print $2}'").split() or [os.cpuCount() or 0])
    return model, cpuCount, coreCount

def getRamInfo():
    #Return CPU model, number of CPUs (sockets), and number of cores
    model = run("free -h | awk '/^Mem:/ {print $2, $7}'").split()
    return (parts[0], parts[1] if len(parts) == 2 else ("N/A", "N/A")


#On to the main!!!
def main():
    #Clear the terminal at the start
    os.system("clear")

    #Set up report basics
    today = datetime.now().strftime("%B &d, %Y")
    hostname = socket.gethostname()
    logfile = os.path.expanduser(f"~/{hostname}_system_report.log")

    #collect everything...
    domain = getDomainSuf()
    ip, mask = getIPandMask()
    gateway = getGateway()
    dns1, dns2 = getDNSservers()
    osName, osVersion, kernel = getOSInfo()
    cpuModel, numcpus, numcores = getCPUInfo()
    ramTotal, ramAvail = getRamInfo()
    diskTotal, diskFree = getDiskInfo()


report = f"""
    System Report - {today}
    ====================================================================

    [Device Information]
        Hostname:            {hostname}
         Domain Suffix:       {domain}

    [Network Information]
        IPv4 Address:        {ip}
        Netmask:             {mask}
        Default Gateway:     {gateway}
        Primary DNS:         {dns1}
        Secondary DNS:       {dns2}

    [Operating System] 
        OS Name:             {osName}
        OS Version:          {osVersion}
        Kernel Version:      {kernel}

    [Storage Information]
        CPU Model:           {cpuModel}
        Number of CPUs:      {numcpus}
        Number of Cores:     {numcores}

    [Memory Information]
        Total RAM:           {ramTotal}
        Available RAM:       {ramAvail}

     [Disk Information]
        Total Disk Space:    {diskTotal}
        Free Disk Space:     {diskFree}

    """

    print(report)

    with open(logfile, "w") as f:
            f.write(report)
        

if __name__=="__main__":
    main()

                                                                                                                                      123,0-1       Bot

