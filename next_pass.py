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
    tp.add_argument("--duration", dest = "duration", action = "store", type = float,  default=6 , help = "Prediction Window [hours]")
    tp.add_argument("--start_ts", dest = "start_ts", action = "store", type = str, default=None , help = "Start Time Stamp, UTC, Format: YYYY-MM-DD HH:MM:SS")
    tp.add_argument("--stop_ts",  dest = "stop_ts",  action = "store", type = str, default=None , help = "Stop Time Stamp, UTC, Format: YYYY-MM-DD HH:MM:SS")

    args = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------
    os.system('reset')
    print 'args:', args

    #creat timescale
    ts = sf.load.timescale()
    #Time Stamp Options:
    #if duration == value, start = none, stop = None
    try:
        if   ((args.start_ts == None) and (args.stop_ts == None)):
            start = datetime.datetime.utcnow()
            duration = int(args.duration * 60 * 60)
        elif ((args.start_ts != None) and (args.stop_ts == None)):    #if start = timestamp, duration == value, stop ==None
            #ts_format = "%Y-%m-%d %H:%M:%S.%f"
            start = datetime.datetime.strptime(args.start_ts, "%Y-%m-%d %H:%M:%S")
            duration = int(args.duration * 60 * 60)
        elif ((args.start_ts != None) and (args.stop_ts != None)):
            start = datetime.datetime.strptime(args.start_ts, "%Y-%m-%d %H:%M:%S")
            stop  = datetime.datetime.strptime(args.stop_ts , "%Y-%m-%d %H:%M:%S")
            duration = int((stop - start).total_seconds())
        #if start == timestamp, stop = timestamp
    except Exception as e:
        print 'Timestamp Exception: {:s}'.format(e)
    #get current utc time
    print "Time Parameters:"
    print "     Start: {:s}".format(str(start))
    if args.stop_ts != None: print "      Stop: {:s}".format(str(stop))
    print "  Duration: {:d}".format(duration)
    #setup range of seconds - # of hours to seconds
    sec_vec = range(int(duration))
    #print sec_vec
    t_vec = ts.utc( start.year,
                    start.month,
                    start.day,
                    start.hour,
                    start.minute,
                    sec_vec)
    #setup ground station
    gs = sf.Topos(latitude_degrees=args.gs_lat,
                  longitude_degrees=args.gs_lon,
                  elevation_m=args.gs_alt)

    #setup satellite
    stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
    satellites = sf.load.tle(stations_url)
    sat = satellites[args.norad_id]

    #difference vector between satellite and ground station
    # format is TO minus FROM
    dif = sat-gs
    rv = dif.at(t_vec)
    [el,az,rho] = rv.altaz()

    #print el.degrees[0], el.degrees[-1]
    above_horizon = el.degrees > 0
    indicies, = above_horizon.nonzero()

    boundaries, = numpy.diff(above_horizon).nonzero()
    aos_los_indices = boundaries.reshape(len(boundaries) // 2, 2)

    passes = []
    print '______________________________________________________________'
    print '|        |            Time           |  Az   |  El  | Range  |'
    print '|--------|---------------------------|-------|------|--------|'
    for i in range(len(aos_los_indices)):
        event = {}
        aos = aos_los_indices[i][0]
        los = aos_los_indices[i][1]
        event['el'] = el.degrees[aos:los]
        tca = numpy.argmax(event['el'])
        event['time'] = t_vec[aos:los].utc_datetime()
        event['velocity'] = rv.velocity.km_per_s[aos:los]
        event['az'] = az.degrees[aos:los]
        event['rho'] = rho.km[aos:los]

        #print event['state_vector'][tca].velocity
        passes.append(event)

    for i, p in enumerate(passes):
        tca_idx = numpy.argmax(p['el'])
        tca_el = p['el'][tca_idx]
        tca_az = p['az'][tca_idx]
        tca_rho = p['rho'][tca_idx]
        tca = p['time'][tca_idx]

        print '| aos {:2d} | {:s} | {:5.1f} | {:4.1f} | {:6.1f} |'.format(i, str(p['time'][0]), p['az'][0], p['el'][0], p['rho'][0])
        print '| tca {:2d} | {:s} | {:5.1f} | {:4.1f} | {:6.1f} |'.format(i, str(tca), tca_az, tca_el, tca_rho)
        print '| los {:2d} | {:s} | {:5.1f} | {:4.1f} | {:6.1f} |'.format(i, str(p['time'][-1]), p['az'][-1], p['el'][-1], p['rho'][-1])
        print '--------------------------------------------------------------'
        #print p['velocity'][tca_idx]
        #for j in range(len(p['time'])):
        #    print p['time'][j], \
        #          p['az'][j], \
        #          p['el'][j], \
        #          p['rho'][j]

    sys.exit()
    for i in range(len(t)):
        vec_dot = dif.at(t[i]).velocity.km_per_s
        range_rate = numpy.linalg.norm(vec_dot)
        print t[i].utc_datetime(), \
              az.degrees[i], \
              el.degrees[i], \
              rho.km[i], \
              range_rate, \
              vec_dot



    sys.exit()
