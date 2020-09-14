import serial
import pandas as pd
import time

import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'..','Utility Classes'))))

from master import TestPoint,Range

class F5730A:
    
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
        self.Model = 'Fluke 5730A'
        self.Ranges=self.CreateRanges()

        self.ser.write(b'REMOTE\r\n')
        self.ser.write(b'*RST\r\n')  

        
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
            
            print (commands)
            
            for command in commands:
                
                self.ser.write(command.encode()+b'\r\n')
                
            self.CurrentRange=TargetRange.Name

            
        else:
            print ('Not Found',RangeName,self.Ranges)
        
        

    def disconnect(self):
        if self.ser.isOpen():
            self.ser.write(b'LOCAL\r\n')
            self.ser.close()
        
        
    def read(self,Command):
        
        self.ser.write(Command+b'\r\n')
        
        while self.ser.inWaiting()==0:
            time.sleep(0.5)
            
        output=self.ser.read(self.ser.inWaiting())
        
        return output

            
    def identity(self):        
        return self.read(b'*IDN?')
    
    def customNoResponse(self,code):
        self.ser.write(code+'\r\n')
        

    def Operate(self):
        results = self.read(b'*ESR?')

        if not self.ConfirmOperate():
            self.ser.write(b'OPER\r\n')
        
        self.SettleOutput()
        
        return "Ready"
    
    def Standby(self):
        
        self.ser.write(b'STBY\r\n')
        self.SettleOutput()

        return "<Danger> Unit is in Operate Mode <Danger>"
    
    def SetExtSense(self,ON=True):
        
        if ON == True:
            self.ser.write('EXTSENSE ON\r\n')
            time.sleep(0.25)
            self.read('*OPC?')
            
            return "External Sense On"
        else:
            self.ser.write('EXTSENSE OFF\r\n')
            time.sleep(0.25)
            self.read('*OPC?')
            
            return "External Sense Off"

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