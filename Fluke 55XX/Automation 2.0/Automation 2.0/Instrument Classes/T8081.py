import serial
import pandas as pd
import time


import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'..','Utility Classes'))))

from master import TestPoint,Range


class T8081:
    
    def __init__(self,comport='COM4'):
        self.ser= serial.Serial(
                        port=comport,
                        baudrate=9600,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,
                        xonxoff=True
                    )
        
        self.CurrentRange=''
        self.Ranges=[]
        
        self.Model="Transmille 8081"
        
        self.Ranges=self.CreateRanges()
        
    def CreateRanges(self):
        
        Ranges={}
        
        df_ranges=pd.read_excel('Ranges.xlsx',sheet_name=self.Model)
        
        for index,row in df_ranges.iterrows():
            
            Ranges[row['Function Name']]=Range(row['Function Name'],row['Primary Unit'],row['Primary Limit Low'],
                                     row['Primary Limit High'],row['Secondary Unit'],row['Secondary Limit Low'],
                                     row['Secondary Limit High'],row['Command'])
            
        return Ranges
        
        
        
    def read(self,Command):
        
        self.ser.write(Command+b'\r\n')

        while self.ser.inWaiting()==0:
            time.sleep(0.5)

        time.sleep(0.5)

        output=self.ser.read(self.ser.inWaiting())
        
        return output
        
    def disconnect(self):
        self.ser.close()
        
        
    def TakeReading(self):
        reading = self.read(b'READ?').decode('ascii')
        reading=str(reading).strip('\r\n')

        try: 
            reading=float(reading.split('E')[0].strip('+'))*10**int(reading.split('E')[1])
        except:
            reading=0.0


        return reading
        
    def WriteRange(self,Range,TP):
        
        if "DC Voltage" in Range.getName():
            self.setDCVoltage(Range)
            
    def Status(self):
        command = 's'
        print (self.read(command.encode()))
        
    def SetRange(self,TP,RangeName):
        
        if RangeName in self.Ranges:

            TargetRange=self.Ranges[RangeName]
            
            commands = TargetRange.CompileCommand(TP)
            
            for command in commands:
                
                print (command)
                self.read(command.encode()+b'\r\n')
                
            self.CurrentRange=TargetRange.Name

            
        else:
            print ('Not Found')