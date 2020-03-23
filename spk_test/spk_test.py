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
    parser = argparse.ArgumentParser(description="SPK/BSP File Loader Test Script",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cwd = os.getcwd()
    cfg_fp_default = '/'.join([cwd, 'config'])
    cfg = parser.add_argument_group('Configuration File')
    cfg.add_argument('--data_path',
                       dest='data_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'data']),
                       help="Camera Configuration File Path",
                       action="store")
    cfg.add_argument('--spk_file',
                       dest='spk_file',
                       type=str,
                       default="2523620.bsp",
                       help="Configuration File",
                       action="store")
    args = parser.parse_args()
    #--------END Command Line argument parser------------------------------------------------------

    #subprocess.run(["reset"])
    if not os.path.exists(args.data_path):
        print('Data path doesn\'t exist: {:s}'.format(args.data_path))
        os.makedirs(args.data_path)
    load = sf.Loader(args.data_path, verbose=True)
    #load timescale object
    ts = load.timescale()

    #setup SPK/BSP file path
    fp_spk = '/'.join([args.data_path,args.spk_file])
    print (fp_spk)
    if not os.path.isfile(fp_spk) == True:
        print('ERROR: Invalid SPK/BSP File Path: {:s}'.format(fp_spk))
        sys.exit()
    print('Importing configuration File: {:s}'.format(fp_spk))
    #load SPK/BSP
    e = load(fp_spk)
    print(e)


    sys.exit()
