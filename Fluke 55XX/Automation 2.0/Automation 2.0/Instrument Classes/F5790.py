import serial
import pandas as pd
import time
import visa

import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'..','Utility Classes'))))

from master import TestPoint,Range


class F5790:

    def __init__(self,port):
        self.port=port

        rm = visa.ResourceManager()

        self.ser = rm.open_resource('GPIB0::{0}::INSTR'.format(self.port))

        self.ser.write('REMOTE')
        self.ser.write('*CLS')
        self.ser.write('INPUT2')
        self.ser.write("EXTRIG ON")
        
        self.ser.timeout=10000

        self.CurrentRange=''
        self.Ranges=[]
        
        self.Model="Fluke 5790"
        
        self.Ranges=self.CreateRanges()


    def Identity (self):
            return self.ser.query('*IDN?')

    def SetRange(self,TP,RangeName):
        
        if RangeName in self.Ranges:

            TargetRange=self.Ranges[RangeName]
            
            commands = TargetRange.CompileCommand(TP)
            
            for command in commands:
                
                print (command)
                self.ser.write(command)
                
            self.CurrentRange=TargetRange.Name

            
        else:
            print ('Not Found')


        time.sleep(1)

        while self.ReadISR()[15] == '1' :
            time.sleep(0.1)

    def CreateRanges(self):

        Ranges={}
        
        df_ranges=pd.read_excel('Ranges.xlsx',sheet_name=self.Model)
        
        for index,row in df_ranges.iterrows():
            
            Ranges[row['Function Name']]=Range(row['Function Name'],row['Primary Unit'],row['Primary Limit Low'],
                                        row['Primary Limit High'],row['Secondary Unit'],row['Secondary Limit Low'],
                                        row['Secondary Limit High'],row['Command'])
            
        return Ranges

    def TakeReading(self):

        self.ser.write("TRIG")

        print ("Triggered")
        print ("Reading...")

        while self.ReadISR()[15] == '1' :
            time.sleep(0.1)

        self.ser.write("VAL?")

        reading=self.ser.read_raw().decode('ascii')

        try: 
            reading = reading.split(',')[0]
            reading=float(reading.split('E')[0].strip('+'))*10**int(reading.split('E')[1])
        except:
            print (reading)
            reading=0.0

        return reading

    def ReadISR(self):

        self.ser.write("ISR?")

        ISR=self.ser.read_raw().decode('ascii')

        reading = ('{0:016b}'.format(int(ISR)))

        return reading



    def disconnect(self):
        self.ser.close()
