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
import pandas as pd
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

    #create query object
    obj = Horizons(id       = cfg['body']['name'],
                   location = cfg['body']['origin_center'],
                   id_type  = cfg['body']['id_type'],
                   epochs   = cfg['body']['epoch'])
    if cfg['body']['type'] == "vectors":
        vec = obj.vectors()

    #print(vec)
    #print(vec.columns)
    keys = ['datetime_jd', 'x', 'y', 'z', 'vx', 'vy', 'vz']
    pos_keys = ['x','y','z']
    vel_keys = ['vx', 'vy', 'vz']
    t_key = 'datetime_jd'
    #print(np.array(vec[keys]))
    df = pd.DataFrame(np.array(vec[keys]), columns=keys)
    #print(df)

    #Export Data
    data_path = '/'.join([cwd, cfg['data_path']])
    if not os.path.exists(data_path):
        print('Data path doesn\'t exist, creating...: {:s}'.format(fp_load))
        os.makedirs(data_path)
    of = "_".join([cfg['body']['name'],
                   cfg['body']['epoch']['start'].replace(" ", "_"),
                   cfg['body']['epoch']['stop'].replace(" ", "_"),
                   cfg['body']['epoch']['step']])
    of = ".".join([of,"csv"])
    o_fp = "/".join([data_path, of])
    print("Exporting to: {:s}".format(o_fp))
    df.to_csv(o_fp, index=False)
    #print(lro.at(t))
    sys.exit()
