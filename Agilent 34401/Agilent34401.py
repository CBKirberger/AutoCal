# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 15:50:50 2020

@author: tech40
"""


#import serial
import pandas as pd
import time
#from datetime import datetime
import visa
import re

import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'..','Utility Classes'))))

from master import TestPoint,Range


class Agilent34401:
    
    def __init__(self):
        self.address = 'ASRL3::INSTR'                               # Address to find instrument
        rm = visa.ResourceManager()                                 # Open the visa resource manager
        self.instrument = rm.open_resource(self.address)            # Open the instrument at the address
        self.instrument.timeout = 30000                             # Set a maximum wait time for communication with the instrument
        self.instrument.write('*RST')                               # Reset to power on settings
        


        self.CurrentRange=''                                        # Placeholder variable to hold the instruments current range
        self.Model='Agilent 34401A'                                 # The instruments make/model info
        self.Ranges=self.CreateRanges()                             # Run the create ranges function to read in the operation info in the Ranges.xlsx sheet
        
        
    def CreateRanges(self):
        '''
        This function reads the Ranges.xlsx sheet to populate this class with 
        what its functions, ranges, and the commands to access them are.
        '''
        df_ranges=pd.read_excel('Ranges.xlsx',sheet_name=self.Model)
        Ranges = {}
        for index,row in df_ranges.iterrows(): 
            Ranges[row['Function Name']]=Range(row['Function Name'],row['Primary Unit'],row['Primary Limit Low'],
                                     row['Primary Limit High'],row['Secondary Unit'],row['Secondary Limit Low'],
                                     row['Secondary Limit High'],row['Command'])
        return Ranges
        
    def Identify(self):
        '''
        This function returns the identy of the instrument as read out by its
        native command.
        '''
        return self.instrument.query('*IDN?')
        
    
    def disconnect(self):
        '''
        This function disconnects the computer from the instrument.
        '''
        self.instrument.close()
        
        
    def TakeReading(self):
        '''
        This function returns whatever the instrument is currently reading.
        '''
        self.instrument.write('TRIG:SOUR:BUS')
        time.sleep(1)
        self.instrument.write('INIT')
        time.sleep(2)
        self.instrument.write('*TRG')
        time.sleep(1)
        reading = self.instrument.query('FETC?')
        
        
        # PARSE AND AVERAGE THE STRING OF READINGS #
        reading = str(reading[:-2]) # get rid of line feed characters
        readList = []
        val = ''
        idx = 0
        excounter = 5
        for c in reading: # for each character
            excounter = excounter + 1
            if c  == 'E': # use the E value like our splitter
                excounter = 0
            if excounter == 4:
                idx = idx + 1
                readList.append(float(val))
                val = ''
            val = val + c
        readList.append(float(val)) # add the last value to the list
        reading = sum(readList)/len(readList) # Take average
        
        return reading
        
    
    def CustomQuery(self,text):
        '''
        Push a custom query to the instrument
        '''
        return self.instrument.query(text)
        time.sleep(0.5)
    
    
    def CustomCommand(self,text):
        '''
        Push a custom command to the instrument
        '''
        self.instrument.write(text)
        time.sleep(0.5)
      
        
    def SetRanges(self,TP,RangeName):
        '''  
            This function is used to configure the Multimeter to the correct
            settings before taking a reading
        '''
        
        if RangeName in self.Ranges:

            TargetRange=self.Ranges[RangeName]
            commands = TargetRange.CompileCommand(TP)

            for command in commands:
                print (command)
                time.sleep(4) # Ensure we don't push too many commands too quickly
                self.instrument.write(command)
                
            self.CurrentRange=TargetRange.Name
            
            # For some reason you have to take a reading to clear the output buffer
            #self.TakeReading()
            
        else:
            print (RangeName + ' not found')
        
        
        
##############################################
        # CLASS AND FUNCTION TESTING #
##############################################
'''     
Ag = Agilent34401()

Ag.instrument.write('*RST')
time.sleep(1)
Ag.instrument.write('FUNC "RES"')
time.sleep(1)
ID = Ag.TakeReading()
print(ID)



Ag.disconnect()
'''