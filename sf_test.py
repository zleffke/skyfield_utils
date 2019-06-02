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
    print args
    ts = sf.load.timescale()
    t = ts.now()
    print t.utc_datetime().hour

    sec_vec = range(10)
    #print sec_vec
    t1 = ts.utc(t.utc_datetime().year,
                t.utc_datetime().month,
                t.utc_datetime().day,
                t.utc_datetime().hour,
                t.utc_datetime().minute,
                sec_vec)

    t = t1
    #t = ts.now()

    planets = sf.load('de421.bsp')
    earth = planets['earth']

    gs = sf.Topos(latitude_degrees=args.gs_lat,
                  longitude_degrees=args.gs_lon,
                  elevation_m=args.gs_alt)
    print gs.at(t).position.km
    print gs.at(t).velocity.km_per_s


    stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
    satellites = sf.load.tle(stations_url)
    #print satellites
    sat = satellites['ISS']
    sat_pos = sat.at(t)
    print 'sat_pos', sat_pos.position.km
    print 'sat_vel', sat_pos.velocity.km_per_s

    dif = sat-gs
    print 'dif', type(dif)
    pos = dif.at(t).position.km
    pos_mag = numpy.linalg.norm(pos)
    vec_dot = dif.at(t).velocity.km_per_s
    range_rate = numpy.linalg.norm(vec_dot)
    print 'vec', vec
    print 'vec_mag', vec_mag
    print 'vec_dot', vec_dot
    print 'vec_dot_mag', range_rate
    [el,az,rho]=dif.at(t).altaz()
    print "el", el.degrees
    print "az", az.degrees
    print "range", rho.km

    for i in range(len(t)):
        vec_dot = dif.at(t[i]).velocity.km_per_s[:,i]
        range_rate = numpy.linalg.norm(vec_dot)
        print t[i].utc_datetime(), \
              az.degrees[i], \
              el.degrees[i], \
              rho.km[i], \
              range_rate, \
              vec_dot



    sys.exit()
















    m = ephem.Moon()

    #--Setup VTGS -----------------
    gs = ephem.Observer()
    gs.lat, gs.lon, gs.elevation = options.gs_lat*deg2rad, options.gs_lon*deg2rad, options.gs_alt

    #--Setup GRAVES -----------------
    graves = ephem.Observer()
    graves.lat = 47.347980*deg2rad
    graves.lon = 5.515095*deg2rad
    graves.elevation = 200

    chain = False

    while 1:
        d = date.utcnow()
        gs.date = d
        m.compute(gs)
        gs_az = dms_to_dec(m.az)
        gs_el = dms_to_dec(m.alt)
        graves.date = d
        m.compute(graves)
        graves_az = dms_to_dec(m.az)
        graves_el = dms_to_dec(m.alt)
        graves_phase = m.moon_phase*100

        if ((gs_el > 0) and (graves_el > 0)): chain = True
        else: chain = False

        os.system('clear')
        print "GRAVES RADAR Lunar Illumination"
        print "Time [UTC]: {:s}".format(str(d))
        print "    GS   Azimuth: {:3.1f}".format(gs_az)
        print "    GS Elevation: {:3.1f}".format(gs_el)
        print "GRAVES   Azimuth: {:3.1f}".format(graves_az)
        print "GRAVES Elevation: {:3.1f}".format(graves_el)
        print "    Chain Status: {:s}".format(str(chain))
        if options.flag == 0:
            print "Libration Lat: {:+3.6f}".format(dms_to_dec(m.libration_lat))
            print "Libration Lon: {:+3.6f}".format(dms_to_dec(m.libration_long))
            print "  Lunar Phase: {:3.3f}%".format(m.moon_phase*100)
        time.sleep(1)





    sys.exit()
