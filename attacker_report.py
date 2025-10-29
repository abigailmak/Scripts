#!/usr/bin/env python3
"""
Abigail Mak 10/29/2025 This is meant to generate a report of IP addresses with 10 or more failed login 
attempts from a provided syslog file (default: /home/student/sys.log) 

- shebang + executable - script commented - clears terminal at run 
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

# GeoIP import
try:
    from geoip import geolite2
except Exception:
    geolite2 = None

# Constantssssss
defaultLogPath = "/home/student/syslog.log"
MinFailures = 10

# regex to find ipv4 addys on lines mentioning failed passwords
ipRegex = re.compile(r'Failed password.*from\s+(\d{1,3}(?:\.\d{1,3}){3})')

# =========================
# Utility functions
# =========================

def clearTerminal():
    #clear the terminal for a clean report
    os.system("clear")


def readLogFile(path):
    #return the contents of the log file as an iterable of lines
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
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
        m = ipRegex.search(line)
        if m:
            ips.append(m.group(1))
    return ips


def getCountryForIP(ip):
    #we're looking up the country code and name for an IP using geoip.geolite2 
    #it also returns a short string (country code or
    if not geolite2:
        return "GeoIP unavailable"
    try:
        match = geolite2.lookup(ip)
        if not match:
            return "Unknown"
        # geolite2.match may have attributes like .country or .country_code depending on version
        country = getattr(match, "country", None)
        if country:
            return country
        country_code = getattr(match, "country_code", None)
        if country_code:
            return country_code
        # fallback not fallout, this is not a band
        return "Unknown"
    except Exception:
        return "Unknown"


def buildReport(ip_counts, min_failures=MinFailures):
    #now we are building the list of all the ips, their countries and their number of failures
    filtered = [(count, ip) for ip, count in ip_counts.items() if count >= min_failures]
    filtered.sort(key=lambda x: x[0])  # sort ascending by count
    #ok lets attach the country info
    report_rows = []
    for count, ip in filtered:
        country = getCountryForIP(ip)
        report_rows.append((count, ip, country))
    return report_rows


def printReport(rows):
    #print formatted report to stdout including the current date
    today = date.today().strftime("%B %d, %Y")
    #lets try colored headers!!!! i love me some skittles
    #taste the rainbow
    print(f"\033[1;32mAttacker Report - {today}\033[0m\n")
    print(f"\033[1;31m{'COUNT':<8}{'IP ADDRESS':<20}{'COUNTRY':<15}\033[0m")
    if not rows:
        print("\nNo IP addresses with 10 or more failed attempts were found.")
        return
    for count, ip, country in rows:
        print(f"{count:<8}{ip:<20}{country:<15}")


def parseArgs():
    #Argument parsing to allow specifying a different log file if desired
    parser = argparse.ArgumentParser(
        description="Generate attacker report from syslog-like file (failed ssh logins)."
    )
    parser.add_argument(
        "-f", "--file",
        default = defaultLogPath,
        help=f"path to syslog file (default: {defaultLogPath})"
    )
    parser.add_argument(
        "-t", "--threshold",
        type=int,
        default=MinFailures,
        help=f"minimum number of failed attempts to include (default: {MinFailures})"
    )
    return parser.parseArgs()


def main():
    args = parseArgs()

    #Step 1 
    clearTerminal()

    #Step 2: read file
    try:
        lines = readLogFile(args.file)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    #Step 3: Extract IPs and count
    ips = extractFailedIPs(lines)
    ip_counts = Counter(ips)

    #Step 4:  Build report with threshold
    report_rows = buildReport(ip_counts, min_failures=args.threshold)

    #Step 5: Print
    printReport(report_rows)


if __name__ == "__main__":
    main()
