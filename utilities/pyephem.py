#!/usr/bin/env python
#########################################
#   Title: pyephem helper utilities     #
# Project: TLE Match                    #
#    Date: Jan 2018                     #
#  Author: Zach Leffke, KJ4QLP          #
#########################################
import sys
import os
import math
import string
import struct
import numpy
import scipy
import datetime as dt
import pandas as pd

deg2rad = math.pi / 180
rad2deg = 180 / math.pi
c       = float(299792458)    #[m/s], speed of light

def dms_to_dec(DMS):
    data = str(DMS).split(":")
    degrees = float(data[0])
    minutes = float(data[1])
    seconds = float(data[2])
    if degrees < 0 : DEC = -(seconds/3600) - (minutes/60) + degrees
    else: DEC = (seconds/3600) + (minutes/60) + degrees
    return DEC

def tle_file_input(fp, fn):
    #input:
    #   fp : path to tle file
    #   fn : tle file name
    #output: dict containing satellite TLE data
    path = '/'.join([fp,fn])
    print 'Importing TLE data from: {:s}'.format(path)
    tle = {}
    if os.path.isfile(path) == True:
        with open(path, 'r') as f: tle_data = f.read().strip().splitlines()
        f.close()
        if len(tle_data)%3 != 0:
            print "ERROR: invalid number of lines in TLE data:{:d}".format(len(tle_data))
            print "ERROR: Should be 3 lines per satellite"
            sys.exit()
        #return tle_data
    else:
        print "ERROR: Invalid TLE source file: " + path
        sys.exit()
    print "Found {:d} satellites".format(len(tle_data) / 3)
    for idx, line in enumerate(tle_data):
        #print idx, line
        if idx%3 == 0:
            tle[line] = {}
            tle[line]['line1'] = tle_data[idx+1]
            tle[line]['line2'] = tle_data[idx+2]
    return tle
