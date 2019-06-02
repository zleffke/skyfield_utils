#!/usr/bin/env python
#############################################
#   Title: Doppler measurement utilities    #
# Project: TLE Match                        #
#    Date: Jan 2018                         #
#  Author: Zach Leffke, KJ4QLP              #
#############################################
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

def Import_Doppler_Data(fp, fn):
    #desc:  Imports Doppler data from GNU Radio file
    #input:
    #   fp : path to doppler measurement file
    #   fn : doppler measurement file
    #       Input file data type expects float32 (gnuradio 'float')
    #       Filename contains Metadata for:
    #           -Satellite Name
    #           -Receiver Type
    #           -Start time in UTC
    #           -sample rate of recording
    #output:
    #   returns pandas dataframe with timestamp for each offset measurement
    path = '/'.join([fp,fn])
    if not (os.path.isfile(path)):
        print "ERROR: Invalid Doppler Measurement source file: " + path
        sys.exit()

    print 'Importing Doppler data from: {:s}'.format(path)
    #Extract File metadata from filename
    md = Get_Meas_File_Metadata(fn)
    print '      Recording Start Time [UTC]: {:s}'.format(str(md['start_ts']))
    print 'Recording Sample Rate [samp/sec]: {:d}'.format(md['samp_rate'])
    print ' Inter-Sample Time Spacing [sec]: {:f}'.format(md['samp_spacing'])

    data_pts = gr_f32_file_input(path)

    ts = []
    idx = []
    print 'Generating Time Stamps'
    for idx, dp in enumerate(data_pts):
        if idx % 1000000 == 0:
            print "Percentage Complete: {:f}".format(float(idx)/len(data_pts)* 100)
        ts.append(md['start_ts'] + dt.timedelta(seconds=idx*md['samp_spacing']))

    df = pd.DataFrame({ 'timestamp':ts,
                        'doppler_offset':data_pts})
    df['doppler_offset'] = df['doppler_offset'].astype(float)
    df.name = md['sat_name']
    return df

def Get_Meas_File_Metadata(filename):
    #input: Doppler Measurement File
    #Filename Format expected, no checks in this function:
    #<SAT NAME>_<RECEIVER TYPE>_YYYYMMDD_HHMMSS.ssssss_<TIME ZONE>_<SAMPLE RATE>.dop

    data = filename.split("_")
    data[-1] = data[-1].strip('.f32')
    md = {} #metadata dict
    md['sat_name'] = data[0]
    md['receiver'] = data[1]
    ts_fmt = "%Y%m%d %H%M%S.%f UTC"
    ts_str = " ".join(data[2:5])
    md['start_ts'] = dt.datetime.strptime(ts_str, "%Y%m%d %H%M%S.%f UTC")
    md['samp_rate_str'] = data[5]
    if 'k' in md['samp_rate_str']:
        md['samp_rate']=int(md['samp_rate_str'].strip('k'))*1000
    elif 'M' in data[5]:
        md['samp_rate']=int(md['samp_rate_str'].strip('M'))*1000000
    elif 'sps' in data[5]:
        md['samp_rate']=int(md['samp_rate_str'].strip('sps'))

    md['samp_spacing'] = 1/float(md['samp_rate'])
    return md

def gr_f32_file_input(fp, verbose = 0):
    #desc:  Imports GNU Radio Float32 File
    #input:  full path to file, assumes is valid
    #output: list of floats for doppler data

    #import gnuradio float32 type, uses scipy
    f = scipy.fromfile(open(fp, 'r'), dtype=scipy.float32)
    if verbose: print "Found {:d} 32 bit floats".format(len(f))
    return f
