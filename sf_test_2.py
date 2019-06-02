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
    parser = argparse.ArgumentParser(description="Data Recorder",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    h_gs_lat    = "Ground Station Latitude [deg]"
    h_gs_lon    = "Ground Station Longitude [deg]"
    h_gs_alt    = "Ground Station Altitude [m]"
    h_flag      = "Lunar/Solar Flag, 0=Lunar,1=Solar [default=%default]"

    gs = parser.add_argument_group('Ground Station')
    gs.add_argument("--gs_lat", dest = "gs_lat", action = "store", type = float, default='37.229977' , help = h_gs_lat)
    gs.add_argument("--gs_lon", dest = "gs_lon", action = "store", type = float, default='-80.439626', help = h_gs_lon)
    gs.add_argument("--gs_alt", dest = "gs_alt", action = "store", type = float, default='610'       , help = h_gs_alt)

    args = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------
    os.system('reset')
    print args

    #creat timescale
    ts = sf.load.timescale()
    #get current utc time
    t = ts.now()
    #setup range of seconds - 1 day
    sec_vec = range(6 *60 *60)
    #print sec_vec
    t1 = ts.utc(t.utc_datetime().year,
                t.utc_datetime().month,
                t.utc_datetime().day,
                t.utc_datetime().hour,
                t.utc_datetime().minute,
                sec_vec)
    t = t1
    t = ts.now()

    #setup ground station
    gs = sf.Topos(latitude_degrees=args.gs_lat,
                  longitude_degrees=args.gs_lon,
                  elevation_m=args.gs_alt)
    #print gs.at(t).position.km
    #print gs.at(t).velocity.km_per_s

    #setup satellite
    stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
    satellites = sf.load.tle(stations_url)
    #print satellites
    sat = satellites['ISS']

    #difference vector between satellite and ground station
    # format is TO minus FROM
    dif = sat-gs
    state_vector = dif.at(t)
    [el,az,rho]=state_vector.altaz()
    #print "el", el.degrees
    #print "az", az.degrees
    #print "range", rho.km

    [x,y,z] = state_vector.position.km
    print 'x', x
    print 'y', y
    print 'z', z

    vel = state_vector.velocity.km_per_s
    [xd, yd, zd] = vel
    print 'xd', xd
    print 'yd', yd
    print 'zd', zd



    sys.exit()
    for i in range(len(vel[0])):
        print t[i].utc_datetime(), numpy.linalg.norm(vel[:,i])

    sys.exit()

    print el.degrees[0], el.degrees[-1]
    above_horizon = el.degrees > 0
    indicies, = above_horizon.nonzero()

    boundaries, = numpy.diff(above_horizon).nonzero()
    aos_los_indices = boundaries.reshape(len(boundaries) // 2, 2)
    print state_vector.velocity.km_per_s.size

    passes = []
    for i in range(len(aos_los_indices)):
        event = {}
        aos = aos_los_indices[i][0]
        los = aos_los_indices[i][1]
        event['el'] = el.degrees[aos:los]
        tca = numpy.argmax(event['el'])
        event['time'] = t[aos:los].utc_datetime()
        event['velocity'] = state_vector.velocity.km_per_s[aos:los]
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

        print 'tca {:d}:'.format(i), tca, tca_az, tca_el, tca_rho
        print p['velocity'][tca_idx]
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
