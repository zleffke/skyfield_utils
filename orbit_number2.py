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
    parser = argparse.ArgumentParser(description="SkyField Satellite Pass Calculator",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    h_gs_lat    = "Ground Station Latitude [deg]"
    h_gs_lon    = "Ground Station Longitude [deg]"
    h_gs_alt    = "Ground Station Altitude [m]"

    gs = parser.add_argument_group('Ground Station Parameters')
    gs.add_argument("--gs_lat", dest = "gs_lat", action = "store", type = float, default='37.229977' , help = "Ground Station Latitude [deg]")
    gs.add_argument("--gs_lon", dest = "gs_lon", action = "store", type = float, default='-80.439626', help = "Ground Station Longitude [deg]")
    gs.add_argument("--gs_alt", dest = "gs_alt", action = "store", type = float, default='610'       , help = "Ground Station Altitude [m]")

    sc = parser.add_argument_group('Spacecraft Parameters')
    sc.add_argument("--norad_id", dest = "norad_id", action = "store", type = int, default=25544 , help = "Spacecraft NORAD ID")

    tp = parser.add_argument_group('Time Parameters')
    tp.add_argument("--duration", dest = "duration", action = "store", type = float,  default=90 , help = "Prediction Window [min]")
    tp.add_argument("--tar_time", dest = "tar_time", action = "store", type = str, default=None , help = "Target Time Stamp, UTC, Format: YYYY-MM-DD HH:MM:SS")

    parser.add_argument("--verbosity",  dest = "verbosity",  action = "store", type = int, default=0 , help = "Verbosity, print pass table?")

    args = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------
    os.system('reset')
    #print 'args:', args

    #creat timescale
    ts = sf.load.timescale()

    #setup satellite
    stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
    satellites = sf.load.tle(stations_url)
    sat = satellites[args.norad_id]
    epoch = (sat.epoch.utc_datetime()).replace(tzinfo=None)

    with open ("stations.txt", "r") as myfile:
        data=myfile.readlines()

    #find revolution number
    rev_num = []
    for line in data:
        if ("2 " + str(sat.model.satnum)) in line:
            rev_num.append(int(line[63:68]))

    #orbital period
    op_min = 1 / (sat.model.no / (2*math.pi))
    op_sec = op_min*60.0
    now = datetime.datetime.utcnow()
    tar_time = datetime.datetime.strptime(args.tar_time, "%Y-%m-%d %H:%M:%S")
    duration = (now - epoch).total_seconds()
    print "       rev num at epoch:", rev_num[-1]
    print "                  epoch:", epoch
    print "                    now:", now
    print "                 target:", tar_time
    print "               duration:", duration
    print "   orbital period [min]:", op_min
    print "   orbital period [sec]:", op_sec

    t_epoch = epoch.replace(tzinfo=sf.utc)
    sec_vec = range(t_epoch.second,t_epoch.second + int(duration))
    #print sec_vec
    t_vec = ts.utc( t_epoch.year,
                    t_epoch.month,
                    t_epoch.day,
                    t_epoch.hour,
                    t_epoch.minute,
                    sec_vec)

    rv1 = sat.at(t_vec)
    subpoint = rv1.subpoint()
    ss_lat = subpoint.latitude.degrees
    ss_lon = subpoint.longitude.degrees
    print '\nRV 1'
    #print t_vec.utc_datetime()
    #print "satellite position [km]:", rv1.position.km.T
    #print "sub-satellite lat [deg]:", ss_lat
    #print "sub-satellite lon [deg]:", ss_lon

    print len(ss_lat)
    asign = numpy.sign(ss_lat)
    signchange = ((numpy.roll(asign, 1) - asign) != 0).astype(int)
    signchange[0] = 0
    print len(signchange), signchange
    locs = numpy.where(signchange == 1)
    print locs


    rev_num
    asc_node_idx = [] #crossing ascending node index
    for i in locs[0]:
        print i, ss_lat[i-1], ss_lat[i], numpy.sign(ss_lat[i] - ss_lat[i-1])
        if numpy.sign(ss_lat[i] - ss_lat[i-1]) > 0: #ascending node
            rev_num.append(rev_num[-1] + 1)
            asc_node_idx.append(i)

    print asc_node_idx
    print rev_num

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
    ax1.set_xlabel('Seconds since epoch')
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
