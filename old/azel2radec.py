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


deg2rad = math.pi / 180
rad2deg = 180 / math.pi
c       = float(299792458)    #[m/s], speed of light

if __name__ == '__main__':
    #--------START Command Line option parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="Convert AZ, EL to RA,DEC",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    h_gs_lat    = "Ground Station Latitude [deg]"
    h_gs_lon    = "Ground Station Longitude [deg]"
    h_gs_alt    = "Ground Station Altitude [m]"
    h_gs_loc    = "Ground Station City/State Location"

    gs = parser.add_argument_group('Ground Station Parameters')
    gs.add_argument("--gs_lat", dest = "gs_lat", action = "store", type = float, default='37.148729'  , help = "Ground Station Latitude [deg]")
    gs.add_argument("--gs_lon", dest = "gs_lon", action = "store", type = float, default='-80.578413' , help = "Ground Station Longitude [deg]")
    gs.add_argument("--gs_alt", dest = "gs_alt", action = "store", type = float, default='584'        , help = "Ground Station Altitude [m]")
    gs.add_argument("--gs_loc", dest = "gs_loc", action = "store", type = str, default='Fairlawn,VA', help = "Ground Station City/State Location")

    args = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------
    os.system('reset')
    print 'args:', args

    #setup ground station
    gs = sf.Topos(latitude_degrees=args.gs_lat,
                  longitude_degrees=args.gs_lon,
                  elevation_m=args.gs_alt)

    print gs

    # apparent = astrometric.apparent()
    # ra, dec, distance = apparent.radec()
    # print(ra.hstr())
    # print(dec.dstr())
    # print(distance)

    ts = sf.load.timescale()
    now_dt = datetime.datetime.utcnow()
    now = ts.utc( now_dt.year,
                  now_dt.month,
                  now_dt.day,
                  now_dt.hour,
                  now_dt.minute,
                  now_dt.second)
    now1 = ts.now()
    print now, now1, now_dt





    sys.exit()
