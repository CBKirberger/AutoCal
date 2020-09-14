# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 13:51:47 2020

This instrument class is for the FLuke 1586 Super DAQ


Currently this class only includes options to read data as that was all that
was required at the time of creation. In the future additional functionality
may be added to this class if it is deemed necessary or desireable.
"""

import serial
import pandas as pd
import time
from datetime import datetime
import visa


from master import TestPoint,Range


class F1586():

    def __init__(self):
        self.address = 'COM3'
        rm = visa.ResourceManager()
        self.instrument = rm.open_resource(self.address)
        self.instrument.timeout = 30000



        self.CurrentRange=''
        self.Model='Fluke 1586 Super DAQ'
        #self.Ranges=self.CreateRanges()
        
        
    def TakeReading(self,channel):
        #cmd = 'DATA:@'+str(channel)+'?'
        #cmd = 'CONF:TEMP THER,RT,(@101)/n/r'
        cmd = 'CONF:TEMP TC,K,(@102)/n/r'
        self.instrument.write(cmd)
        reading = self.instrument.query('READ?')
        
        #reading = self.instrument.write()
        #reading = self.instrument.write('FETC?/n')
        print(reading)

        return reading

    def disconnect(self):
        self.instrument.close()

##############
# Testing the class
################
    
DAQ = F1586()
Output = DAQ.TakeReading(1)

DAQ.disconnect()


