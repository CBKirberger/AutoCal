import serial
import pandas as pd
import time
import visa

import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'..','Utility Classes'))))

from master import TestPoint,Range


class F8508:

    def __init__(self,port):
        self.port=port
        self.FunctionMap=['V','A','OHM','MOHM']

        rm = visa.ResourceManager()

        self.ser = rm.open_resource('GPIB0::{0}::INSTR'.format(self.port))
        
        self.ser.write('*RST')
        
        time.sleep(15)

        self.ser.write('REMOTE')
        self.ser.write("TRG_SRCE EXT")

        self.ser.timeout=4294967294

        self.CurrentRange=''
        self.Ranges=[]
        
        self.Model="Fluke 8508A"
        
        self.Ranges=self.CreateRanges()


    def Identity (self):
            return self.read('*IDN?')

    def CreateRanges(self):
    
        Ranges={}
        
        df_ranges=pd.read_excel('Ranges.xlsx',sheet_name=self.Model)
        
        for index,row in df_ranges.iterrows():
            
            Ranges[row['Function Name']]=Range(row['Function Name'],row['Primary Unit'],row['Primary Limit Low'],
                                        row['Primary Limit High'],row['Secondary Unit'],row['Secondary Limit Low'],
                                        row['Secondary Limit High'],row['Command'])
            
        return Ranges

    def read(self,Command):
        
        self.ser.write(Command)
        
        while self.ser.inWaiting()==0:
            time.sleep(0.25)
            
        output=self.ser.read(self.ser.inWaiting())
        
        return output


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

    def setinputDCV(self,Range="AUTO",Filter="FILT_OFF",resolution="RESL5",fast="FAST_ON",Input="TWO_WR"):


        if not self.InputCheck(Filter,["FILT_ON","FILT_OFF"]):
            return "Invalid Filter Type: FILT_ON or FILT_OFF"

        if not self.InputCheck(resolution,["RESL5","RESL6","RESL7","RESL8"]):
            return "Invalid Resolution: RESL5,RESL6, RESL7, RESL8"

        if not self.InputCheck(fast, ["FAST_ON","FAST_OFF"]):
            return "Invalid Fast Option: FAST_ON or FAST_OFF"

        if not self.InputCheck(Input,["TWO_WR","FOUR_WR"]):
            return "Wrong Wire Selection: Choose TWO_WR or FOUR_WR"

        self.ser.write("DCV {0},{1},{2},{3},{4}".format(Range,Filter,resolution,fast,Input))


        return "Output Set"

    def setinputACV(self,Range="AUTO",Filter="FILT40HZ",resolution="RESL6",tfer="TFER_ON",coupling="ACCP",spot="SPOT_OFF",Input="TWO_WR"):
        

        if not self.InputCheck(Filter,["FILT100HZ","FILT40HZ","FILT10HZ","FILT1HZ"]):
            return "Wrong Filter Selection: Choose FILT1HZ, FILT10HZ, FILT40HZ, FILT100HZ"

        if not self.InputCheck(resolution,["RESL5","RESL6"]):
            return "Wrong Resolution: 5.5 or 6.5 Digit"

        if not self.InputCheck(tfer,["TFER_ON","TFER_OFF"]):
            return "Wrong TFER: TFER_ON,TFER_OFF"

        if not self.InputCheck(coupling,["ACCP","DCCP"]):
            return "Wrong Coupling: ACCP,DCCP"
        
        if not self.InputCheck(spot,["SPOT_ON","SPOT_OFF"]):
            return "Wrong Frequency Correction: SPOT_ON,SPOT_OFF"

        if not self.InputCheck(Input, ["TWO_WR","FOUR_WR"]):
            return "Wrong Terminal Selection: TWO_WR,FOUR_WR"

        self.ser.write("ACV {0},{1},{2},{3},{4},{5},{6}".format(Range,Filter,resolution,tfer,coupling,spot,Input))
        time.sleep(1)

        return "Output Set"

    def setinputNormalOhm(self,Range="Auto",Filter="FILT_OFF",resolution="RESL7",fast="FAST_ON",Input="TWO_WR",LO_I="LOI_OFF"):

        if not self.InputCheck(Filter,["FILT_ON","FILT_OFF"]):
            return "Wrong Filter Selection: FILT_ON or FILT_OFF"
        
        if not self.InputCheck(resolution,["RESL5","RESL6","RESL7","RESL8"]):
            return "Wrong Resolution Selection: RESL5, RESL6, RESL7, or RESL8"

        if not self.InputCheck(fast,["FAST_ON","FAST_OFF"]):
            return "Wrong Fast Selection: FAST_ON or FAST_OFF"
        
        if not self.InputCheck(Input,["TWO_WR","FOUR_WR"]):
            return "Wrong Input Selection: TWO_WR or FOUR_WR"

        if not self.InputCheck(LO_I,["LOI_ON","LOI_OFF"]):
            return "Wrong LO_I Selection: LOI_ON or LOI_OFF"

        self.ser.write("OHMS {0},{1},{2},{3},{4},{5} \r\n".format(Range,Filter,resolution,fast,Input,LO_I))
        time.sleep(1)

        return "Output Set"

    
    def setinputHVOhm(self,Range="Auto",Filter="FILT_OFF",resolution="RESL7",fast="FAST_OFF",Input="TWO_WR"):

        if not self.InputCheck(Filter,["FILT_ON","FILT_OFF"]):
            return "Wrong Filter Selection: FILT_ON or FILT_OFF"
        
        if not self.InputCheck(resolution,["RESL5","RESL6","RESL7","RESL8"]):
            return "Wrong Resolution Selection: RESL5, RESL6, RESL7, or RESL8"

        if not self.InputCheck(fast,["FAST_ON","FAST_OFF"]):
            return "Wrong Fast Selection: FAST_ON or FAST_OFF"
        
        if not self.InputCheck(Input,["TWO_WR","FOUR_WR"]):
            return "Wrong Input Selection: TWO_WR or FOUR_WR"


        self.ser.write("HIV_OHMS {0},{1},{2},{3},{4} \r\n".format(Range,Filter,resolution,Input,fast))
        time.sleep(1)

        return "Output Set"


    def setinputTrueOhm(self,Range="Auto",resolution="RESL7",fast="FAST_ON",LoI="LOI_OFF"):

        '''        
        if not self.InputCheck(resolution,["RESL5","RESL6","RESL7","RESL8"]):
            return "Wrong Resolution Selection: RESL5, RESL6, RESL7, or RESL8"

        if not self.InputCheck(fast,["FAST_ON","FAST_OFF"]):
            return "Wrong Fast Selection: FAST_ON or FAST_OFF"

        if not self.InputCheck(LoI,["LOI_ON","LOI_OFF"]):
            return "Wrong LO_I Selection: LOI_ON or LOI_OFF"
        '''
        
        self.ser.write("TRUE_OHMS {0},{1},{2},{3} \r\n".format(Range,resolution,fast,LoI))
        time.sleep(1)

        return "Input Set"

    def setinputDCA(self,Range="Auto",resolution="RESL7",fast="FAST_ON",Filter="FILT_ON"):

        if not self.InputCheck(resolution,["RESL5","RESL6","RESL7"]):
            return "Wrong Resolution Selection: RESL5, RESL6, RESL7"

        if not self.InputCheck(fast,["FAST_ON","FAST_OFF"]):
            return "Wrong Fast Selection: FAST_ON or FAST_OFF"

        if not self.InputCheck(Filter,["FILT_ON","FILT_OFF"]):
            return "Wrong Fast Selection: FAST_ON or FAST_OFF"


        
        self.ser.write("DCI {0},{1},{2},{3} \r\n".format(Range,Filter,resolution,fast))
        time.sleep(1)

        return "Output Set"

    def setinputACA(self,Range="Auto",resolution="RESL6",coupling="ACCP",Filter="FILT40HZ"):

        if not self.InputCheck(resolution,["RESL5","RESL6"]):
            return "Wrong Resolution Selection: RESL5, RESL6"

        if not self.InputCheck(Filter,["FILT1HZ","FILT10HZ","FILT40HZ","FILT100HZ"]):
            return "Wrong Fast Selection: FILT1HZ, FILT10HZ, FILT40HZ, or FILT100HZ"

        if not self.InputCheck(coupling,["ACCP","DCCP"]):
            return "Wrong LO_I Selection: ACCP or DCCP"


        self.ser.write("ACI {0},{1},{2},{3} \r\n".format(Range,Filter,resolution,coupling))
        time.sleep(1)

        return "Output Set"

    def SetInput(self,InputType="FRONT"):
        '''FRONT, REAR , DIV_REAR, SUB_REAR, DEVTN, OFF'''

        if not self.InputCheck(InputType,["FRONT","REAR","DIV_REAR","SUB_REAR","DEVTN","OFF"]):
            return "Wrong InputType Selection: FRONT, REAR , DIV_REAR, SUB_REAR, DEVTN, OFF"

        self.ser.write ("INPUT {0}".format(InputType))

        time.sleep(1)

        return "Input Type Set"

    def TakeReading(self):

        self.ser.write('*MESE 0x80')

        self.ser.write("*TRG")

        self.ser.query('MESR?')

        self.ser.write("RDG?")

        reading=self.ser.read_raw().decode('ascii')

        print (reading)

        try: 
            reading=float(reading.split('E')[0].strip('+'))*10**int(reading.split('E')[1])
        except:
            reading=0.0


        return reading


    def PerformZero(self,Function=False):

        if Function:
            self.ser.query('MZERO?')
        else:
            self.ser.query('ZERO?')

    def disconnect(self):
        self.ser.close()

        return 'Zeroed'
