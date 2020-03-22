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
from skyfield.api import utc
from astroquery.jplhorizons import Horizons
from astropy import units as u

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
                       default="lro_occult_config.json",
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
    moon = e['moon']
    #print(e)
    #setup ground station
    gs = sf.Topos(latitude_degrees=cfg['gs']['latitude'],
                  longitude_degrees=cfg['gs']['longitude'],
                  elevation_m=cfg['gs']['altitude'])
    print(cfg['gs']['name'], gs)

    #create query object
    obj = Horizons(id       = cfg['body']['name'],
                   location = cfg['body']['origin_center'],
                   id_type  = cfg['body']['id_type'],
                   epochs   = cfg['body']['epoch'])
    if cfg['body']['type'] == "vectors":
        vec = obj.vectors()
    #print(vec)
    print(vec.columns)
    keys = ['datetime_jd', 'x', 'y', 'z', 'vx', 'vy', 'vz']
    pos_keys = ['x','y','z']
    vel_keys = ['vx', 'vy', 'vz']
    t_key = 'datetime_jd'
    #print(np.array(vec[pos_keys])[0])
    #print(np.array(vec[t_key])[0])
    t = ts.tdb(jd=np.array(vec[t_key])[0])
    #print(vec['datetime_str'][0], t.tt, t.tdb)

    for i, t in enumerate(vec[t_key]):
        #t = ts.tdb(jd=np.array(vec[t_key])[0])
        t_step = ts.tdb(jd=t)
        print (t_step, t_step.tdb, t_step.utc_iso())
        lro = skyfield.positionlib.Geocentric(tuple(vec[pos_keys][i]),
                                              tuple(vec[vel_keys][i]),
                                              t=t_step,
                                              center=cfg['body']['origin_center'],
                                              target=-85)
        print('lro', lro)
        #print(lro.position.km)
        #rv = (e['earth']+gs).at(t)


        geo_rv = gs.at(t_step)
        od = skyfield.vectorlib.ObserverData()
        gs._snag_observer_data(od, t_step)
        od.gcrs_position = geo_rv.position
        
        print(od.altaz_rotation, od.ephemeris, od.gcrs_position)
        print('gs', geo_rv)
        dif = lro - geo_rv
        dif = skyfield.positionlib.Geometric(dif.position,
                                             dif.velocity,
                                             observer_data=od)
        print(dif)
        print(dif.altaz())
        #print(dif.apparent())
        #print(dif.altaz())

    #print(lro.distance())

    #print(lro.at(t))
    sys.exit()
