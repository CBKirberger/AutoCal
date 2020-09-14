import serial
import pandas as pd
import time
from datetime import datetime

import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'..','Utility Classes'))))

from master import TestPoint,Range

class F5522A:
    
    def __init__(self,comport='COM4'):
        self.ser= serial.Serial(
                        port=comport,
                        baudrate=9600,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,
                        xonxoff=False,
                        rtscts=False
                    )
        
        self.CurrentRange=''
        self.Model = 'Fluke 5522A'
        self.Ranges=self.CreateRanges()
        self.logger=open('F5522_Log.txt','w')

        self.write(b'REMOTE\n')
        self.write(b'*CLS\n')

        

        
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
            
            if not self.CurrentRange==RangeName:
                self.Standby()


            TargetRange=self.Ranges[RangeName]
            commands = TargetRange.CompileCommand(TP)

            for command in commands:
                
                self.write(command.encode()+b'\n')
                
            self.CurrentRange=TargetRange.Name

            
        else:
            print ('Not Found',RangeName,self.Ranges)
        
    def disconnect(self):
        if self.ser.isOpen():
            self.write(b'LOCAL\n')
            self.Standby()
            self.ser.close()
            self.logger.close()
                
    def read(self,Command):
        
        self.write(Command+b'\n')

        while (self.ser.in_waiting == 0):
            time.sleep(0.1)

        self.logger.write("{0}: Reading {1}\n".format(datetime.now(),repr(Command.decode('ascii'))))
        output=self.ser.read_until('\n',self.ser.in_waiting)
        self.logger.write("{0}: Read {1}\n".format(datetime.now(),repr(output.decode('ascii'))))

        return output

    def write(self,Command):

        self.logger.write("{0}: Write {1}\n".format(datetime.now(),repr(Command.decode('ascii'))))
        print (repr(Command))
        self.ser.write(Command)

        self.ser.flush()

        time.sleep(0.1)

    def identity(self):        
        return self.read(b'*IDN?')

        
    def Operate(self):

        if not self.ConfirmOperate():
            self.write(b'*CLS\n')
            self.write(b'OPER\n')
        
        self.SettleOutput()
        
        return "Ready"
    
    def Standby(self):
        
        self.write(b'STBY\n')
        self.SettleOutput()

        return "<Danger> Unit is in Operate Mode <Danger>"
    

    def getOutputValue(self):
        value=self.read('OUT?')
        result=value.split(',')

        reading = str(result[0])
        reading=reading.strip('\n')
        reading=reading.replace('+','')
        reading=float(reading.split('E')[0])*10**(float(reading.split('E')[1]))
        result[0] = reading

        reading = str(result[2])
        reading=reading.strip('\n')
        reading=reading.replace('+','')
        reading=float(reading.split('E')[0])*10**(float(reading.split('E')[1]))
        result[2] = reading

        return result

    def SettleOutput(self):
        
        #The ISR Command checks the event register.  It returns the decimal equivalent to a 16 digit binary code.  The .format function converts the integer to a string.
        #We are interested in the 12th binary digit, or the 3rd index of the string.  When it is 1 the output is settled, when it is not...we wait until it is.  
        
        time.sleep(1)
        settled=self.getBinaryOutput()[3]

        while int(settled)==0:
            settled=self.getBinaryOutput()[3]
            time.sleep(0.5)
            
        print ('Output Settled')
            
            
    def ConfirmOperate(self):
        
        #The ISR Command checks the event register.  It returns the decimal equivalent to a 16 digit binary code.  The .format function converts the integer to a string.
        #We are interested in the 12th binary digit, or the 3rd index of the string.  When it is 1 the output is settled, when it is not...we wait until it is.  
        
        time.sleep(1)
        settled=self.getBinaryOutput()[15]
        
        print (settled)

        if settled == '1':
            print ("Confirmed Operate")
            return True 
        else:
            return False
        
    def ConfirmStandBy(self):
        
        #The ISR Command checks the event register.  It returns the decimal equivalent to a 16 digit binary code.  The .format function converts the integer to a string.
        #We are interested in the 12th binary digit, or the 3rd index of the string.  When it is 1 the output is settled, when it is not...we wait until it is.  
        
        time.sleep(1)
        settled=self.getBinaryOutput()[15]
        
        print (settled)

        if settled == '0':
            print ("Confirmed Operate")
            return True 
        else:
            return False
    
    def getBinaryOutput(self):
        ISR=self.read(b'ISR?')
        ISR = (int(ISR.decode('ascii')))
        return '{0:016b}'.format(ISR)

    def Statuses(self):

        ISR=self.read(b'ISR?')
        ISR = (int(ISR.decode('ascii')))
        print ('ISR: {0:016b}'.format(ISR))

        ISR=self.read(b'*STB?')
        ISR = (int(ISR.decode('ascii')))
        print ('STB: {0:08b}'.format(ISR))

        ISR=self.read(b'*ESR?')
        ISR = (int(ISR.decode('ascii')))
        print ('ESR: {0:08b}'.format(ISR))

    def ReadError(self):

        Error = self.read(b'ERR?')

        print (Error.decode('ascii'))

    def SetCommands(self,commands):

            commands = commands.split('|')

            for command in commands:
                self.write(command.encode()+b'\n')


