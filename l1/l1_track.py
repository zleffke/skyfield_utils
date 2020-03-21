#! /usr/bin/python3

import sys
import os
import math
import string
import argparse
import json
import subprocess
import datetime
import time
import numpy
from spktype21 import SPKType21
import skyfield
from skyfield import api as sf
from skyfield import almanac
from skyfield import jpllib
from astropy import units as u


#from PyQt5 import QtGui, QtCore, QtWidgets
#from gui.spinner import *

deg2rad = math.pi / 180
rad2deg = 180 / math.pi
c       = float(299792458)    #[m/s], speed of light
au2km   = 149597870.700 #km/au
day2sec = 86400 #seconds/day

if __name__ == "__main__":
    """ Main entry point to start the service. """
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="VTGS Camera Client",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cwd = os.getcwd()
    cfg_fp_default = '/'.join([cwd, 'config'])
    cfg = parser.add_argument_group('Configuration File')
    cfg.add_argument('--cfg_path',
                       dest='cfg_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'config']),
                       help="Camera Configuration File Path",
                       action="store")
    cfg.add_argument('--cfg_file',
                       dest='cfg_file',
                       type=str,
                       default="config.json",
                       help="Configuration File",
                       action="store")
    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------

    #subprocess.run(["reset"])

    #print(sys.path)
    fp_cfg = '/'.join([args.cfg_path,args.cfg_file])
    print (fp_cfg)
    if not os.path.isfile(fp_cfg) == True:
        print('ERROR: Invalid Configuration File: {:s}'.format(fp_cfg))
        sys.exit()
    print('Importing configuration File: {:s}'.format(fp_cfg))
    with open(fp_cfg, 'r') as json_data:
        cfg = json.load(json_data)
        json_data.close()

    print (cfg)
    #set up data path
    fp_load = '/'.join([cwd, cfg['data_path']])
    if not os.path.exists(fp_load):
        print('Skyfield data path doesn\'t exist: {:s}'.format(fp_load))
        os.makedirs(fp_load)
    load = sf.Loader(fp_load, verbose=True)
    #load timescale object
    ts = load.timescale()
    #load almanac
    e = load('de421.bsp')
    earth = e['earth']
    sun = e['sun']
    print('Earth:', earth)
    print('  Sun:', sun)

    fp_bsp = '/'.join([cwd, cfg['data_path'], cfg['bsp_file']])
    if not os.path.isfile(fp_bsp) == True:
        print('ERROR: Invalid BSP File: {:s}'.format(fp_bsp))
        sys.exit()
    k21 = SPKType21.open(fp_bsp)
    spkid = k21.segments[0].target
    print(k21, type(k21))
    print("Target ID:", spkid)
    #sys.exit()
    #setup ground station
    gs = sf.Topos(latitude_degrees=cfg['gs']['latitude'],
                  longitude_degrees=cfg['gs']['longitude'],
                  elevation_m=cfg['gs']['altitude'])
    print(cfg['gs']['name'], gs)

    t = ts.utc(datetime.datetime.now(datetime.timezone.utc)) #Now
    pos21, vel21 = k21.compute_type21(0, spkid, t.tt) #pos - km, vel km/s

    #pos21 = pos21 *u.km
    pos21 = pos21 / au2km #Convert poistion from km to AU
    print(pos21)
    sys.exit()
    # km/s * sec/day * au/km
    vel21 = vel21 / au2km * day2sec #converts vel from km/s to au/day
    #print(vel21)
    l1 = skyfield.positionlib.Barycentric(pos21, vel21, t=t.tt, center=0, target=spkid)
    earth_bary = earth.at(t)
    sun_bary = sun.at(t)
    gs_bary = (e['earth']+gs).at(t)
    print('Earth:', earth_bary)
    print(earth_bary.position)
    print('  Sun:', sun_bary)
    print(sun_bary.position)
    print("   L1:", l1)
    print(pos21)
    print(l1.position)
    print('   GS:', gs_bary)
    print(gs_bary.position)
    #sys.exit()
    dif = (l1-gs_bary)
    print('dif', type(dif), dif)
    print(dif.position.km)
    pos_mag = numpy.linalg.norm(dif.position.km)
    print(pos_mag)
    [el,az,rho]=dif.altaz()
    print("Elevation:", el.degrees)
    print("  Azimuth:", az.degrees)
    #print(rv.position.km)
    sys.exit()



    #t = ts.utc(datetime.datetime.now(datetime.timezone.utc)) #Now

    #print (pos21, vel21)


    print(l1.position, l1.velocity)
    gs_rv = (e['earth']+gs).at(t)
    print("GS Pos/Vel:", gs_rv)
    print(gs_rv.position, gs_rv.velocity)

    dif = l1 - gs_rv
    print (dif.position.km)
    pos_mag = numpy.linalg.norm(dif.position.km)
    print (pos_mag)

    sys.exit()

    while True:
        t = ts.utc(datetime.datetime.now(datetime.timezone.utc)) #Now
        #print (t.tt)
        pos21, vel21 = k21.compute_type21(0, spkid, t.tt)
        #print (pos21, vel21)
        l1 = skyfield.positionlib.Barycentric(pos21, vel21, t=t.tt, target=spkid)
        print("L1 Pos/Vel:", l1)
        print(l1.position, l1.velocity)
        gs_rv = (e['earth']+gs).at(t)
        print("GS Pos/Vel:", gs_rv)
        print(gs_rv.position, gs_rv.velocity)

        dif = l1 - gs_rv
        print (dif.position.km)
        pos_mag = numpy.linalg.norm(dif.position.km)
        print (pos_mag)
        time.sleep(1)


    sys.exit()
    #Setup Search Time
    rise_set = Lunar_Rise_Set(e,gs)
    #print (rise_set)

    if rise_set['vis']:
        try:
            while True:
                subprocess.run(["clear"])
                t = ts.utc(datetime.datetime.now(datetime.timezone.utc)) #Now
                time_to_set = (rise_set['set']-t.utc_datetime())#.total_seconds()
                astrometric = (e['earth']+gs).at(t).observe(e['moon'])
                alt, az, d = astrometric.apparent().altaz()
                t_c = d.km * 1000 / c
                lunar_illum = Lunar_Illumination(e, t)
                #print(alt.degrees, az.degrees, d.km, time_to_set)
                print("Moon is Visible!")
                print("  Current Azimuth [deg]: {:3.2f}".format(az.degrees))
                print("Current Elevation [deg]: {:3.2f}".format(alt.degrees))
                print("     Current Range [km]: {:3.2f}".format(d.km))
                print("   1 Way Prop Delay [s]: {:3.6f}".format(t_c))
                print("   2 Way Prop Delay [s]: {:3.6f}".format(t_c*2))
                print(" Lunar Illumination [%]: {:3.3f}".format(lunar_illum * 100))
                print("            Time to Set: {:s}".format(str(time_to_set)))

                time.sleep(1)
        except KeyboardInterrupt:
            print('interrupted!')
    else:
        while True:
            subprocess.run(["clear"])
            print('Moon not currently visible')
            t = ts.utc(datetime.datetime.now(datetime.timezone.utc)) #Now
            time_to_rise = (rise_set['rise']-t.utc_datetime())#.total_seconds()
            print ("Next Moon Rise:", rise_set['rise'])
            print ("Time to Moon Rise:", time_to_rise)
            time.sleep(1)
