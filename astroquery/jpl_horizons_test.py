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
import skyfield
import numpy as np
from skyfield import api as sf
from skyfield import almanac

from astroquery.jplhorizons import Horizons



#from PyQt5 import QtGui, QtCore, QtWidgets
#from gui.spinner import *

deg2rad = math.pi / 180
rad2deg = 180 / math.pi
c       = float(299792458)    #[m/s], speed of light

if __name__ == "__main__":
    """ Main entry point to start the service. """
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="Download HORIZONS data and store in file",
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
    print('Earth:', type(earth))
    print('  Sun:', type(sun))

    t = ts.utc(datetime.datetime.now(datetime.timezone.utc)) #Now
    print(sun.at(t))
    print(sun.at(t).observe(earth))

    #sys.exit()
    epochs={'start':'2020-03-21 00:00:00', 'stop':'2020-03-21 01:00:00', 'step':'1m'}
    obj = Horizons(id='LRO', location='500@0', id_type='majorbody', epochs=epochs)
    vec = obj.vectors()
    print(vec)
    print(vec.columns)
    column_keys = ['datetime_jd', 'x', 'y', 'z', 'vx', 'vy', 'vz']
    pos_keys = ['x','y','z']
    vel_keys = ['vx', 'vy', 'vz']
    t_key = 'datetime_jd'
    print(np.array(vec[pos_keys])[0])
    lro = skyfield.positionlib.Barycentric(np.array(vec[pos_keys]),
                                           np.array(vec[vel_keys]),
                                           t=np.array(vec[t_key]), center=0, target=-85)
    print(lro.distance())
    #print(lro.at(t))
    sys.exit()
