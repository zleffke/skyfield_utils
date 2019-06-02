#!/usr/bin/env python
#############################################
#   Title: Satellite utilities              #
# Project: TLE Match                        #
#    Date: Jan 2018                         #
#  Author: Zach Leffke, KJ4QLP              #
#############################################
import sys
import os
import math
import string
import struct
import numpy
import scipy
import ephem
import datetime as dt
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import *


deg2rad = math.pi / 180
rad2deg = 180 / math.pi
c       = float(299792458)    #[m/s], speed of light

def Doppler_Shift(center_freq, range_rate):
    #Returns Doppler Shift at receiver given fixed emitter
    #center_freq [Hz]:  center frequency of emitter
    #range_rate [m/s]:  range rate between emitter and receiver, negative means approaching
    #         c [m/s]:  speed of light
    #c = float(299792458) #[m/s], speed of light
    f_obs = (1.0 - range_rate / c) * center_freq
    f_delta = -1.0 * range_rate / c * center_freq
    doppler = {}
    doppler['center'] = f_obs
    doppler['offset'] = f_delta
    #return f_obs, f_delta
    return doppler

def Doppler_Shift_Invert(f_obs, range_rate):
    #Returns frequency of emitted signal given
    #      f_obs [Hz]:  measured or observed frequency
    #center_freq [Hz]:  center frequency of emitter
    #range_rate [m/s]:  range rate between emitter and receiver
    center_freq = f_obs / (1 - range_rate/c)
    return center_freq

def Freq_2_Lambda(frequency):
    #Frequency passed in Hertz
    c = 299792458 #[m/s]
    lam = c / frequency
    return lam

def Path_Loss(link_range, lam, n = 2):
    #link range - length of path in meters
    #lam         - operating wavelength in meters
    #n            - path loss exponent, exp = 2 for free space
    #loss = n*10*log10(4*pi*link_range / lam)
    loss = n*10*math.log10(4*math.pi*link_range / lam)
    return loss

def lin_inv_xpndr_map(up, up_min = 145.900e6, up_max = 146.000e6, dn_min = 435.800e6, dn_max = 435.900e6):
    #Linear Inverting Transponder Uplink to Downlink Mapping
    #Default Values for FO-29 in Hz
    dn = dn_max - (up - up_min) * (dn_max - dn_min) / (up_max - up_min)
    return dn

def lin_inv_xpndr_map_reverse(dn, up_min = 145.900e6, up_max = 146.000e6, dn_min = 435.800e6, dn_max = 435.900e6):
    #Linear Inverting Transponder Downlink to Uplink Mapping
    #Default Values for FO-29 in Hz
    up = (dn_max - dn) * (up_max - up_min) / (dn_max - dn_min) + up_min
    return up


class satellite(object):
    def __init__(self, ephem_sat, sat_name, norad_id):
        self.ephem_sat  = ephem_sat     #PyEphem Satellite object for use in computations
        self.sat_name   = sat_name #Common Name of spacecraft
        self.norad_id   = norad_id #NORAD ID of spacecraft

    def gen_doppler(self, gs, timestamp, rx_freq):
            #input:  pyephem GS object
        #--convert timestamp to useable datetime format
        timestamp=[dt.datetime.utcfromtimestamp(element*1e-9) for element in timestamp]
        #print timestamp
        measured_freq = []
        doppler_offset = []

        for ts in timestamp:
            gs.date = ephem.Date(ts) #convert datetime to ephem date
            self.ephem_sat.compute(gs)
            range_rate = self.ephem_sat.range_velocity
            doppler = Doppler_Shift(rx_freq, range_rate)
            #print ts, range_rate, doppler['center'], doppler['offset']
            measured_freq.append(doppler['center'])
            doppler_offset.append(doppler['offset'])

        df = pd.DataFrame({ 'timestamp':timestamp,
                            'doppler_offset':doppler_offset,
                            'measured_freq':measured_freq})
        df['doppler_offset'] = df['doppler_offset'].astype(float)
        df['measured_freq'] = df['measured_freq'].astype(float)

        df.name = self.sat_name +'('+ self.norad_id + ')'
        return df
