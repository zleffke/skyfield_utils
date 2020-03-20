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
from skyfield import api as sf
from skyfield import almanac



#from PyQt5 import QtGui, QtCore, QtWidgets
#from gui.spinner import *

deg2rad = math.pi / 180
rad2deg = 180 / math.pi
c       = float(299792458)    #[m/s], speed of light

def Lunar_Rise_Set(e, gs, t0=None, t1=None):
    if t0== None:
        t0 = ts.utc(datetime.datetime.now(datetime.timezone.utc)) #Now
    if t1 == None:
        t1 = ts.utc(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)) #24 hours from now
    #print(t0)
    #print(t1)
    f = almanac.risings_and_settings(e, e['Moon'], gs)
    t, y = almanac.find_discrete(t0, t1, f)
    #print (t, y)
    for ti, yi in zip(t, y):
        #print (ti,yi)
        print('Lunar Rise:' if yi else ' Lunar Set:', ti.utc_datetime())
        if yi: #Rise
            rise_time = ti.utc_datetime()
        else:
            set_time = ti.utc_datetime()

    return {'rise':rise_time,
             'set':set_time,
             'vis':set_time < rise_time}

def Lunar_Illumination(e,t):
    fi = almanac.fraction_illuminated(e, 'Moon', t)
    return fi


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
    #load timescale object
    ts = sf.load.timescale()
    #load almanac
    e = sf.load('de421.bsp')
    print(e)
    #setup ground station
    gs = sf.Topos(latitude_degrees=cfg['gs']['latitude'],
                  longitude_degrees=cfg['gs']['longitude'],
                  elevation_m=cfg['gs']['altitude'])
    print(cfg['gs']['name'], gs)

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
            print('Moon not visible')
            t = ts.utc(datetime.datetime.now(datetime.timezone.utc)) #Now
            time_to_rise = (rise_set['rise']-t.utc_datetime())#.total_seconds()
            print ("Time to Moon Rise:", time_to_rise)
