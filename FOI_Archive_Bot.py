#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 @snehankekre
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Usage:
# python FOI_Archive_Bot.py -f from_request -t to_request -r retries -l log_file.txt
#
# Install:
# pip install requests archiveis stem

import sys
import time
import requests
import archiveis
import socks
import socket
import argparse

# Python controller library for Tor
import stem.process
from stem.util import term

# very hacky code
__version__ = '0.1-dev'

print (term.format("[*] Loading script... ", term.Attr.BOLD))
print "[*]"
print "[*]                   ___"
print "[*]                   `. \ "
print "[*]                     \_) "
print "[*]     ____ _,..OOO......\...OOO-...._ ___ "
print "[*]   .`    '_.-(  9``````````P  )--...)   `. "
print "[*]  ` ((     `  || __         ||   `     )) ` "
print "[*] (          ) |<`  ````---__||  (          ) "
print "[*]  `        `  ||) ,xx  xx.  //)__`        ` "
print "[*]   `-____-`   ,/  O`  O`   //,'_ )`-____-` "
print "[*]            ,/     ,,     //  |// "
print "[*]           /      ((          // "
print "[*]          (   (._    _,)     (_) -OH YEAH!"
print "[*]           \    \````/        /     FREEDOM OF INFORMATION!"
print "[*]             \_   _____   __/ "
print "[*]               | |     | | "
print "[*]              (   )   (   ) "
print "[*]            ,--'~'\   /'~'--, "
print "[*]           (_______) (_______) "
print "[*]"
print "[*]  -ps. bring out the RUM!\n"


parser = argparse.ArgumentParser(description=
    "A bot that archives Freedom of Information Requests from https://righttoknow.org.au (https://github.com/snehankekre/FOI_Archive_Bot) version %s" % __version__,
                                 usage='%(prog)s -s from_request -e to_request -r retries -l log_urls_to_file.txt')
                                 
parser.add_argument('-s', '--start', required=True, metavar='from_request', type=int, default=1,
                    help='FOI request number to start archiving from (default=1)')
                    
parser.add_argument('-e', '--end', required=True, metavar='to_request', type=int, default=5000,
                    help='FOI request number to stop archiving at (default=5000')
                    
parser.add_argument('-r', '--retries', required=True, metavar='retries', type=int, default=3,
                    help='set max number of retries when bot encounters a connection error (default=3)')

parser.add_argument('-l', '--log', metavar='log_urls_to_file',
                    help='log archived urls to a file')

args = parser.parse_args()

SOCKS_PORT = 9050

# Set socks proxy
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
socket.socket = socks.socksocket

def print_bootstrap_lines(line):
  if "Bootstrapped " in line:
    print(term.format(line, term.Color.GREEN, term.Attr.BOLD))


print(term.format("Starting Tor:", term.Attr.BOLD))

tor_process = stem.process.launch_tor_with_config(
  config = {
    'SocksPort': str(SOCKS_PORT),
    'ExitNodes': '{de}, {nl}',
  },
  init_msg_handler = print_bootstrap_lines,
)


# Perform DNS resolution through the socket
def getaddrinfo(*args):
  return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

socket.getaddrinfo = getaddrinfo

# Check Python version
if sys.version_info[0] > 2:
    raise Exception("Must be using Python 2.7")


# Set max number of connection retries
args.retries = 3

# Flag: Only archive existent pages
FLAG = True

# Set number of requests to archive from righttoknow.org.au
FOIA_REQUESTS = 5000

def internet_archive(linkToArchive, connection_attempt, MAX_RETRIES, FLAG):

    save_url = "https://web.archive.org/save/%s" % linkToArchive
    
    print("[+] Uploading to Wayback Machine...")
    
    # Upload request to archive.is server
    response = requests.get(save_url) #todo: catch all the exceptions! haven't been able to reliably reproduce the BadStatusLines httplib error.
    
    
    if response.status_code == 200:
        # record URL relevant to the archive page
        result = response.headers['Content-Location']
        
        # build archive URL 
        internet_archive_url = "https://web.archive.org%s" % result
        return internet_archive_url

    else:
        print "[!] Connection error"
        print "[!] Retrying...\n"
        
        if connection_attempt <= MAX_RETRIES:
		    connection_attempt += 1
		    internet_archive(linkToArchive, connection_attempt, MAX_RETRIES, FLAG)
        else:
		    print "[!] retry limit exceeded"
		    print "[!] Right to Know FOI request page probably does not exist anymore"
		    print "[!] Moving on to next request...\n"
		    FLAG = False
		    return FLAG


def main():
    output_file = open(args.log, 'w')
    for request in range (args.start, args.end+1):
        if FLAG:
            connection_attempt = 1
            linkToArchive = "https://www.righttoknow.org.au/request/" + str(request) #todo: figure out non-naive way to do this. archive human readable urls instead?
        
            # print link being currently archived
            print "\n[*] Given FOI request URL to archive: %s" % linkToArchive
        
            # archive the URL
            internet_archive_url = internet_archive(linkToArchive, connection_attempt, args.retries, FLAG)
        
            # push to archive.is
            print "[+] Uploading to archive.is..."
            archiveis_result = archiveis.capture(linkToArchive).replace("http", "https")     
        
            print "[+] FOI Request Archived %s" % linkToArchive
            print "[+] Wayback Machine: %s" % str(internet_archive_url)
            print "[+] archive.is: %s \n" % str(archiveis_result)
            
            # save links to file
            if args.log:
                    output_file.write(str(internet_archive_url))
        else:
		    continue
		# sleep to avoid bot triggers
        time.sleep(0.3)

    output_file.close()
    
	# kill Tor process on completion
    tor_process.kill()

    print "[*] %d FOI requests archived on the Wayback Machine" % (args.end - args.start + 1)
    print "[*] Links saved to file: %s\n"  % args.log
    print "[*] Killed Tor process"
    print "[*] Exiting..."
    return True

if __name__ == "__main__":
    main()
