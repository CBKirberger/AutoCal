# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 09:10:34 2020

Agilent 34401 Calibration Procedure

This script is designed to perform a full calibration of the Agilent 34401
Multimeter.

Last Edited By - Clayton Kirberger
"""

import pandas as pd
import time
import visa
import re
import numpy as np

from master import TestPoint,Range
from Agilent34401 import Agilent34401
#from F5730A import F5730A

# Load and initialize some important data and objects #
UUT = Agilent34401() # Create the UUT object
#Fluke5730 = F5730A() # Create the Fluke 5730 object
TestPoints = pd.read_excel('TestPoints_Parsed_34401.xlsx')
Ranges = pd.read_excel('Ranges.xlsx','Agilent 34401A')


#############################################################
# Calibration routine for 4 wire front short
#############################################################
print('Begining calibration routine for the Agilent 34401 Multimeter.\n')
print('This calibration requires the Fluke 5730 Calibrator and a Calibration short in addition to the UUT.\n')
print('Short the front 4 terminals of the Agilent 34401 making sure you are shorting Hi with Lo.\n')

UserInput = input('Type "Start" to begin the 2 Wire Front test point group or type "Skip" to skip this test point group: ')
while UserInput != 'Start' and UserInput != 'Skip': # Prevent accidental inputs from begining the calibration
    print('Unknown Input!')
    UserInput = input('Type "Start" to begin the 2 Wire Front test point group or type "Skip" to skip this test point group: ')


if UserInput == 'Start':
    print('\nRunning all 2 Wire Front based test points.\n')

    # Isolate all test points for the group 2W Front
    ActiveTPS = TestPoints[TestPoints['Group'] == 'Front Short']
    
    for row, TP in ActiveTPS.iterrows(): # Run each test point in the group

        if TP['PU'] == 'V' and np.isnan(TP['FV']): # This TP uses the DC voltage range
            ActiveRange = 'DC Voltage Front'
        elif TP['PU'] == 'Ohm':
            ActiveRange = '2W Resistance Front'
        elif TP['PU'] == 'Hz':
            ActiveRange = 'Frequency Accuracy'
        else:
            ActiveRange = 'Test point ' + str(row) + ' range'
        
        TP = TestPoint(TP)
        UUT.SetRanges(TP,ActiveRange)
        TPValue = UUT.TakeReading()
        print(TPValue)
        
    
UUT.disconnect()

