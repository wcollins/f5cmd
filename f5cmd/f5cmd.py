# -*- coding: utf-8 -*-


''' Main entry point to f5cmd '''

__package__ = 'f5cmd'
__version__ = '0.1'

from .ltm import *
from sys import argv

def main():

    args = argv[1:]

    logic(args)

def logic(a):

    option = a[0]

    print "Running: %s \nVersion: %s" % (__package__, __version__)

    if option in {'-h', '--help'}:
        usage()

    if option in {'-c', '--create'}:
        if a[1] in {'-v', '--virtual'}:
            hostname = a[2]
            ltm = ltm_interact(hostname)
            ltm.create_virtual_interact()

        elif a[1] in {'-b', '--bulk'}:
            csv_data = 'data.csv'
            if a[1] in {'-c', '--create'}:
                ltm = ltm_bulk(csv_data)
                ltm.create_virtual_bulk()

    if option in {'-d', '--delete'}:
        if a[1] in {'-v', '--virtual'}:
            hostname = a[2]
            ltm = ltm_interact(hostname)
            ltm.delete_virtual_interact()

        elif a[1] in {'-d', '--bulk'}:
            csv_data = 'data.csv'
            if a[1] in {'-d', '--delete'}:
                ltm = ltm_bulk(csv_data)
                ltm.delete_virtual_bulk()

def usage():

    print '''
f5cmd is a command line tool used to automate routine tasks on f5 Network's
Local Traffic Manager - https://f5.com/products/big-ip/local-traffic-manager-ltm

######################
# f5cmd syntax usage # 
######################

Command structure: python -m f5cmd <action> <argument>

# Possible actions
-c --create
-d --delete
-l --list

# Possible arguments
-v --virtual
-b --bulk

'''
