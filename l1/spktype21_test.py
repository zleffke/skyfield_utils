#! /usr/bin/python3
from spktype01 import SPKType01
from spktype21 import SPKType21
import csv
import numpy as np
import datetime
from skyfield import api as sf
import time

bspfiles = 'Ceres_Vesta.bsp'
csvfiles = ['Ceres_jpl.csv', 'Vesta_jpl.csv']
testnames = ['Ceres', 'Vesta']
bodyids = [2000001, 2000004]

dposlim = 1.0       # position difference limit = 1.0 kilometer
dvellim = 1e-7      # velocity difference limit = 0.0001 m/s

k21 = SPKType21.open('L1_2020_2021-21.bsp')
spkid = k21.segments[0].target
print(k21)
print(spkid)
ts = sf.load.timescale()
while True:
    t = ts.utc(datetime.datetime.now(datetime.timezone.utc)) #Now
    print (t.tt)
    pos21, vel21 = k21.compute_type21(0, spkid, t.tt)
    print (pos21, vel21)
    time.sleep(1)
