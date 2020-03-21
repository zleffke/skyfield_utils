#! /usr/bin/python3
from spktype01 import SPKType01
import csv
import numpy as np

bspfiles = 'Ceres_Vesta.bsp'
csvfiles = ['Ceres_jpl.csv', 'Vesta_jpl.csv']
testnames = ['Ceres', 'Vesta']
bodyids = [2000001, 2000004]

dposlim = 1.0       # position difference limit = 1.0 kilometer
dvellim = 1e-7      # velocity difference limit = 0.0001 m/s

kernel = SPKType01.open('L1_2020_20201_type01.bsp')
print(kernel)
