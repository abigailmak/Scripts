#!/usr/bin/env python3
"""
Abigail Mak
10/29/2025

This is meant to generate a report of IP addresses with 10 or more failed login attempts from a provided syslog file (default: /home/student/sys.log)

- shebang + executable
- script commented
- clears terminal at run
- uses regex to extract IPv4 addresses from "Failed password" lines
- counts and filters IPs having >= 10 failed attempts
- uses geoip.geolite2 to get country of origin
- displays current date, headers, and results sorted in ascending order
- structured, pythonic style with error handling and comments
"""

import os
import re
import sys
from collections import Counter
from datetime import date
import argparse


#GeoIP import
try:
    from geoip import geolite2
except Exception:
    geolite2 = None #worry about it later lol


#the default path 
defaultLogPath = "/home/student/syslog.log"

#regex to find ipv4 addys on lines mentioning failed passwords
ipRegex = re.compile(r'Failed password.*from\s+(\d{1,2}(?:\.d{1,3}){3})')

MinFailures = 10 #threshold


def clearTerminal():
    #clear the terminal for a clean report
    os.system("clear")


def readLogFile(path):
    #return the contents of the log file as an iterable of lines
    try:
        with open(path, "r", encoding = "utf-8", errors = "replace") as fh:
            return fh.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Log file not found: {path}")
    except PermissionError:
        raise PermissionError(f"Permission denied reading log file: {path}")


def extractFailedIPs(lines):
    #here we are extracting the ipv4 addys from lines showing failed login attempts
    #oh this function also returns a list of IP strings
    ips = []
    for line in lines:
        match = ipRegex.search(line)
        if match:
            ip = match.group(1)
            ips.append(ip)
    return ips


def getCountry(ip):
    #we're looking up the country code and name for an IP using geoip.geolite2
    #it also returns a short string (country code or unknown if no country)
    if not geolite2:
        return "GeoIP unavailable"

    try:
        match = geolite2.lookup(ip)
        if not match:
            return "Unknown"
        #ok we are attempting to get a readable country val here
        country = getattr(match, "country", None)
        if country:
            return country
        countryCode = getattr(match, "countryCode", None)
        if countryCode:
            return countryCode
        countryName = getattr(match, "countryName", None)
        if countryName:
            return countryName
        return "Unknown"
    except Exception:
        return "Unknown"


def buildReport(ipCounts, minFailures = MinFailures):
    #now we are building the list of all the ips, their countries and their number of failures
    filtered = [(count, ip) for ip, count in ipCounts.items() if count >= minFailures]
    #we are sorting ascending by fount (first element of tuple)
    filtered.sort(key = lambda x: x[0])
    #ok lets attach the country info
    reportRows = []
    for count, ip in filtered:
        country = getCountryForIP(ip)
        reportRows.append((count, ip, country))
    return reportRows


def printReport(rows):
    #print formatted report to stdout including the current date
    today = date.today().strftime("%B %d, %Y")
    #lets try colored headers
    print(f"\033[1;32mAttacker Report - {today}\033[0m\n")
    print(f"\033[1;31m{'COUNT':<8}{'IP ADDRESS':<20}{'COUNTRY':<15}\033[0m")
    if not rows:
        print("\nNo IP addresses with 10 or more failed attempts were found.")
        return

    for count, ip, country in rows:
        print(f"{count:<9}{ip:<20}{country:<15}")


def parse_args():
    #Argument parsing to allow specifying a different log file if desired
    parser = argparse.ArgumentParser(description = "Generate attacker report from syslog-like file (failed ssh logins).")
    parser.addArgument("-f", "--file", default = defaultLogPath, help = f"minimum number of failed attempts to include (default: {minFailures})")
    return parser.parse_args()

def main():
    args = parse_args()

    #Step 1
    clearTerminal()

    #Step 2
    try:
        lines = readLogFile(args.file)
    except Exception as e:
        print(f"Error: {e}", file = sys.stderr)
        sys.exit(2)

    #Step 3
    ips = extractFailedIPs(lines)

    #Step 4
    ipCounts = Counter(ips)

    #Step 5
    reportRows = buildReport(ipCounts, minFailures = args.threshold)

    #Step 6
    printReport(reportRows)


if __name__=="__main__":
    main()
