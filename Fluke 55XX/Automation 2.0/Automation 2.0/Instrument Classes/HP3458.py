import serial
import pandas as pd
import time
import visa

import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'..','Utility Classes'))))

from master import TestPoint,Range

class HP3458():

    def __init__(self,port):
        self.port=port

        rm = visa.ResourceManager()

        self.ser = rm.open_resource('GPIB0::{0}::INSTR'.format(self.port))
                
        self.ser.timeout=5000
        
        self.ser.write("RESET")
        self.ser.write("TARM HOLD;END ALWAYS")

        self.CurrentRange=''

        self.Ranges=[]
        
        self.Model="HP 3458"
        
        self.Ranges=self.CreateRanges()

    def CreateRanges(self):
    
        Ranges={}
        
        df_ranges=pd.read_excel('Ranges.xlsx',sheet_name=self.Model)
        
        for index,row in df_ranges.iterrows():
            
            Ranges[row['Function Name']]=Range(row['Function Name'],row['Primary Unit'],row['Primary Limit Low'],
                                        row['Primary Limit High'],row['Secondary Unit'],row['Secondary Limit Low'],
                                        row['Secondary Limit High'],row['Command'])
            
        return Ranges

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

    def TakeReading(self):

        self.ser.write('TARM SGL')

        m=self.ser.query("MCOUNT?")

        reading = []

        for n in range(int(m)):
            reading.append(self.ser.query("RMEM {0}".format(n+1)))

        return reading

    def ReadError(self):

        self.ser.write('ERR?')

        output = self.ser.read()

        return output


    def identity(self):

        self.ser.write('ID?')

        time.sleep(1)

        output = self.ser.read()

        return output

    def disconnect(self):
        self.ser.close()

        return 'Zeroed'