import serial
import pandas as pd
import time
from datetime import datetime
import visa

import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'..','Utility Classes'))))

from master import TestPoint,Range


class K53220A():

    def __init__(self):
        self.address = 'USB0::0x0957::0x1807::MY58020199::INSTR'
        rm = visa.ResourceManager()
        self.instrument = rm.open_resource(self.address)
        self.instrument.timeout = 30000



        self.CurrentRange=''
        self.Model='Keysight 53220A'
        self.Ranges=self.CreateRanges()

    def CreateRanges(self):
        
        Ranges={}
        
        df_ranges=pd.read_excel('Ranges.xlsx',sheet_name=self.Model)
        
        for index,row in df_ranges.iterrows():
            
            Ranges[row['Function Name']]=Range(row['Function Name'],row['Primary Unit'],row['Primary Limit Low'],
                                     row['Primary Limit High'],row['Secondary Unit'],row['Secondary Limit Low'],
                                     row['Secondary Limit High'],row['Command'])
            
        return Ranges

    def Identity(self):
        return self.instrument.query('*IDN?')

    def disconnect(self):
        self.instrument.close()

    def TakeReading(self):

        self.instrument.write('INIT')
        time.sleep(0.5)
        self.instrument.write('*TRG')
        time.sleep(0.5)
        reading = self.instrument.query('FETC?')

        try: 
            reading = reading.split(',')[0]
            reading=float(reading.split('E')[0].strip('+'))*10**int(reading.split('E')[1])
        except:
            print (reading)
            reading=0.0

        return reading



    def CustomQuery(self,text):
        return self.instrument.query(text)

    def CustomCommand(self,text):
        self.instrument.write(text)

        return "Done"


    def SetRange(self,TP,RangeName):
        
        if RangeName in self.Ranges:

            TargetRange=self.Ranges[RangeName]
            commands = TargetRange.CompileCommand(TP)

            for command in commands:
                print (command)
                time.sleep(0.5)
                self.instrument.write(command)
                
            self.CurrentRange=TargetRange.Name

        else:
            print ('Not Found',RangeName,self.Ranges)




    


