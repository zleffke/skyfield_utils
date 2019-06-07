#!/usr/bin/env python
#########################################
#   Title: SkyField Test Program        #
# Project: Lunar Tracking Program
#    Date: Aug 2019                     #
#  Author: Zach Leffke, KJ4QLP          #
#########################################

import math
import string
import time
import sys
import csv
import os
import datetime
import numpy
from skyfield import api as sf
from skyfield.elementslib import osculating_elements_of as oef
import argparse
import pandas as pd

import utilities.plotting

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.dates as mdates
import matplotlib.colors as colors

deg2rad = math.pi / 180
rad2deg = 180 / math.pi
c       = float(299792458)    #[m/s], speed of light

if __name__ == '__main__':
    #--------START Command Line option parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="SkyField orbit number based orbital period",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    h_gs_lat    = "Ground Station Latitude [deg]"
    h_gs_lon    = "Ground Station Longitude [deg]"
    h_gs_alt    = "Ground Station Altitude [m]"

    sc = parser.add_argument_group('Spacecraft Parameters')
    sc.add_argument("--norad_id", dest = "norad_id", action = "store", type = int, default=25544 , help = "Spacecraft NORAD ID")

    tp = parser.add_argument_group('Time Parameters')
    tp.add_argument("--duration", dest = "duration", action = "store", type = float,  default=None , help = "Prediction Window [min]")
    tp.add_argument("--start_ts", dest = "start_ts", action = "store", type = str, default=None , help = "Start Time Stamp, UTC, Format: YYYY-MM-DD HH:MM:SS")
    tp.add_argument("--stop_ts",  dest = "stop_ts",  action = "store", type = str, default=None , help = "Stop Time Stamp, UTC, Format: YYYY-MM-DD HH:MM:SS")

    parser.add_argument("--verbosity",  dest = "verbosity",  action = "store", type = int, default=0 , help = "Verbosity, print pass table?")

    args = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------
    os.system('reset')
    #print 'args:', args
    print "---------------------------------"
    print "INVALID SCRIPT"
    print "True/Mean Anomaly cannot be used to compute ascending node/orbit number"
    print "True/Mean Anomaly is the angle from periapsis, not RAAN"
    print "numpy algorithms are still useful, so keeping script"
    print "--------------------------------"

    stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
    #satellites = sf.load.tle(stations_url, reload=True)
    satellites = sf.load.tle(stations_url)
    sat = satellites[args.norad_id]
    epoch = (sat.epoch.utc_datetime()).replace(tzinfo=None)

    #creat timescale
    ts = sf.load.timescale()
    #Default:  Start = epoch, stop = now
    stop = None
    now = datetime.datetime.utcnow()
    sec_since_epoch = int((now - epoch).total_seconds())

    try:
        #setup start time:
        if (args.start_ts != None):
            if (args.start_ts == 'now'):
                start = now
            else:
                start = datetime.datetime.strptime(args.start_ts, "%Y-%m-%d %H:%M:%S")
        else: #if not specificed start at epoch
            start = (sat.epoch.utc_datetime()).replace(tzinfo=None)

        if (args.stop_ts != None):
            if (args.stop_ts == 'now'):
                stop = now
            else:
                stop  = datetime.datetime.strptime(args.stop_ts , "%Y-%m-%d %H:%M:%S")
        else:
            stop = now

        if (args.duration != None):
            duration = int(args.duration * 60)
            stop = None
        else:
            duration = int((stop - start).total_seconds())

        if duration <= 0:
            print "Problem with duration, check simulation times"
            sys.exit()
        #if start == timestamp, stop = timestamp
    except Exception as e:
        print 'Timestamp Exception: {:s}'.format(e)
        sys.exit()

    print "Time Parameters:"
    print "                  epoch:", epoch
    print "                    now:", now
    print "    Seconds Since Epoch:", sec_since_epoch
    print "                  Start: {:s}".format(str(start))
    if stop != None: print "                   Stop: {:s}".format(str(stop))
    print "    Simulation Duration: {:d}".format(duration)

    #open TLE file, read in all lines
    with open ("stations.txt", "r") as myfile:
        data=myfile.readlines()

    #find revolution number
    rev_num = []
    for line in data:
        if ("2 " + str(sat.model.satnum)) in line:
            rev_num.append(int(line[63:68]))

    #Mean anomaly at Epoch
    ma_rad = sat.model.mo # radians
    ma_deg = ma_rad * 180.0 / numpy.pi

    #orbital period from mean motion
    mm_rad_min = sat.model.no
    mm_rad_sec = mm_rad_min * 1.0 / 60.0
    mm_deg_sec = mm_rad_sec * 180.0 / numpy.pi
    op_min = 1 / (sat.model.no / (2*math.pi))
    op_sec = op_min*60.0
    print "At Epoch:"
    print "     mean anomaly [rad]:", ma_rad
    print "     mean anomaly [deg]:", ma_deg
    print "  mean motion [rad/min]:", mm_rad_min
    print "  mean motion [rad/sec]:", mm_rad_sec
    print "  mean motion [deg/sec]:", mm_deg_sec
    print "       rev num at epoch:", rev_num[-1]
    print "   orbital period [min]:", op_min
    print "   orbital period [sec]:", op_sec

    t_epoch = epoch.replace(tzinfo=sf.utc)

    sec_vec = range(t_epoch.second,sec_since_epoch)
    t_vec = ts.utc( t_epoch.year,
                    t_epoch.month,
                    t_epoch.day,
                    t_epoch.hour,
                    t_epoch.minute,
                    sec_vec)
    #t_vec = t_vec[0:10]
    print "Computing Satellite State Vector:"
    rv1 = sat.at(t_vec)
    subpoint = rv1.subpoint()
    ss_lat = subpoint.latitude.degrees
    ss_lon = subpoint.longitude.degrees

    ta_vec = oef(rv1).true_anomaly.degrees
    ma_vec = oef(rv1).mean_anomaly.degrees

    #signchange = ((ta_vec - numpy.roll(ta_vec, 1)) <= 0).astype(int)
    signchange = numpy.diff(ta_vec)# <= 0).astype(int)
    #print signchange
    #print signchange[0:10]
    locs = list(numpy.where(signchange < -180))
    #print len(locs), locs
    #sys.exit()
    rev_num
    asc_node_idx = [] #crossing ascending node index
    print "these are showing indexs of periapsis:"
    for i in locs[0]:
        print i, ss_lat[i-1], ss_lat[i], numpy.sign(ss_lat[i] - ss_lat[i-1])
        if numpy.sign(ss_lat[i] - ss_lat[i-1]) > 0: #ascending node
            rev_num.append(rev_num[-1] + 1)
            asc_node_idx.append(i)

    #---- START Figure 1 ----
    xinch = 14
    yinch = 7
    fig1=plt.figure(1, figsize=(xinch,yinch/.8))
    ax1 = fig1.add_subplot(1,1,1)
    #Configure Grids
    ax1.xaxis.grid(True,'major', linewidth=1)
    ax1.yaxis.grid(True,'minor')
    ax1.yaxis.grid(True,'major', linewidth=1)
    ax1.yaxis.grid(True,'minor')
    #Configure Labels and Title
    ax1.set_xlabel('Seconds')
    ax1.set_ylabel('True Anomaly [deg]')
    title = 'Ascending Node Identification'
    ax1.set_title(title)
    #Plot Data
    ax1.plot(sec_vec, ta_vec, linestyle = '-', color='b', markersize=1, markeredgewidth=0)
    ax1.plot(sec_vec, ma_vec, linestyle = '-', color='r', markersize=1, markeredgewidth=0)
    #for i,asc_idx in enumerate(locs):
    #    ax1.plot(sec_vec[asc_idx], ss_lat[asc_idx], marker = '*', \
    #             label=str(rev_num[i+1]), color = 'r', \
    #             markersize=10, markeredgewidth=0)
    #    ax1.text(sec_vec[asc_idx]+20, ss_lat[asc_idx]-5,str(rev_num[i+1]))

    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)

    plt.show()


    sys.exit()

    #detect equator crossing
    asign = numpy.sign(ss_lat)
    signchange = ((numpy.roll(asign, 1) - asign) != 0).astype(int)
    signchange[0] = 0
    print len(signchange), signchange
    locs = numpy.where(signchange == 1)
    print locs

    #detect ascending node, increment rev number
    rev_num
    asc_node_idx = [] #crossing ascending node index
    for i in locs[0]:
        print i, ss_lat[i-1], ss_lat[i], numpy.sign(ss_lat[i] - ss_lat[i-1])
        if numpy.sign(ss_lat[i] - ss_lat[i-1]) > 0: #ascending node
            rev_num.append(rev_num[-1] + 1)
            asc_node_idx.append(i)

    #---- START Figure 1 ----
    xinch = 14
    yinch = 7
    fig1=plt.figure(1, figsize=(xinch,yinch/.8))
    ax1 = fig1.add_subplot(1,1,1)
    #Configure Grids
    ax1.xaxis.grid(True,'major', linewidth=1)
    ax1.yaxis.grid(True,'minor')
    ax1.yaxis.grid(True,'major', linewidth=1)
    ax1.yaxis.grid(True,'minor')
    #Configure Labels and Title
    ax1.set_xlabel('Seconds')
    ax1.set_ylabel('Sub-Satellite Latitude [deg]')
    title = 'Ascending Node Identification'
    ax1.set_title(title)
    #Plot Data
    ax1.plot(sec_vec, ss_lat, linestyle = '-', markersize=1, markeredgewidth=0)
    for i,asc_idx in enumerate(asc_node_idx):
        ax1.plot(sec_vec[asc_idx], ss_lat[asc_idx], marker = '*', \
                 label=str(rev_num[i+1]), color = 'r', \
                 markersize=10, markeredgewidth=0)
        #ax1.annotate(str(rev_num[i+1]),
        #             xy=(sec_vec[asc_idx], ss_lat[asc_idx]), xycoords='data',
        #             xytext=(sec_vec[asc_idx]-20, ss_lat[asc_idx]-20), textcoords='data',
        #             arrowprops=dict(facecolor='black', shrink=0.05),
        #             horizontalalignment='right', verticalalignment='top',
        #             )
        ax1.text(sec_vec[asc_idx]+20, ss_lat[asc_idx]-5,str(rev_num[i+1]))

    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)

    plt.show()

    sys.exit()
