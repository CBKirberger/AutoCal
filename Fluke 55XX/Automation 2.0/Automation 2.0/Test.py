import pandas as pd
import numpy as np
import traceback
import time

import sys

import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'Utility Classes'))))
sys.path.append(os.path.abspath((os.path.join(sys.path[0],'Instrument Classes'))))

from F5730A import F5730A
from T8081 import T8081
from F8508 import F8508
from F5522A import F5522A
from F5790 import F5790
from K53220A import K53220A
from HP3458 import HP3458

from master import TestPoint,Range ,slackmessenger

def SelectGroup(df,Group):
        return df[df.Group == Group]


def Calibrate_Capacitance(row,Standard,Calibrator):

    Meter = HP3458(22)

    Params= [row.PV,row.PU,row.PP,row.SV,row.SU,row.SP,row.FV,row.FU,row.FP]

    print (Params)
    TP = TestPoint(Params)

    Calibrator.SetRange(TP,'Capacitance')
    Standard.SetRange(TP,'DC Current - Capacitance')
    
    TP2 = TestPoint('10.00000 V')
    Meter.SetRange(TP2,'DCV 10 V')
    
    Calibrator.Operate()
    Standard.Operate()
    
    data = Meter.TakeReading()
    
    Calibrator.Standby()
    Standard.Standby()

    def parse(reading):
    
        reading = reading['Readings']

        reading=float(reading.split('E')[0].strip('+'))*10**int(reading.split('E')[1])
        
        return reading

    df = pd.DataFrame(np.array(data), columns = ['Readings'])
    df['Readings']=df['Readings'].str.replace('\r\n','')
    df['Readings']=df.apply(parse,axis=1)

    delta_V=df.iloc[0]['Readings']-df.iloc[-1]['Readings']

    Current = TP.ComputeValue('Secondary')


    result = (Current * 9.9) / delta_V


    Reading = result

    
    if float(row['Tolerance_High']) >= TP.BuildFromPrimary(Reading) >= float(row['Tolerance_Low']):
        print ('Pass: ',TP.BuildFromPrimary(Reading))
        row['Disposition']='True'
        row['Reading']=TP.BuildFromPrimary(Reading)
    else:
        print ('Fail: ',TP.BuildFromPrimary(Reading))
        row['Disposition']='False'
        row['Reading']=TP.BuildFromPrimary(Reading)
        ms.Update('Warning, Detected OOT at Test Point: {0} {1} Readings: {2}'.format(row['Function'],row['Nominal'],TP.BuildFromPrimary(Reading)))
    
    time.sleep(2)

    return row


def Calibrate_OhmsLaw(row,Meter,Calibrator,Resistance):
    
    Params= [row.PV,row.PU,row.PP,row.SV,row.SU,row.SP,row.FV,row.FU,row.FP]
    TP = TestPoint(Params)
    
    Calibrator.SetRange(TP,row['CalibratorFunction'])

    if row['CalibratorCommands']:
        Calibrator.SetCommands(row['CalibratorCommands'])
    
    Meter.SetRange(TP,row['MeterFunction'])
    
    Calibrator.Operate()

    Meter.TakeReading()

    Reads=3
    Readings=[]

    for n in range(Reads):
        Readings.append(Meter.TakeReading())

    Reading = sum(Readings)/len(Readings)

    Reading=Reading/Resistance

    if float(row['Tolerance_High']) >= TP.BuildFromPrimary(Reading) >= float(row['Tolerance_Low']):
        print ('Pass: ',TP.BuildFromPrimary(Reading))
        row['Disposition']='True'
        row['Reading']=TP.BuildFromPrimary(Reading)
    else:
        print ('Fail: ',TP.BuildFromPrimary(Reading))
        row['Disposition']='False'
        row['Reading']=TP.BuildFromPrimary(Reading)
        ms.Update('Warning, Detected OOT at Test Point: {0} {1} Readings: {2}'.format(row['Function'],row['Nominal'],TP.BuildFromPrimary(Reading)))
    
    time.sleep(2)

    return row
    

def Calibrate(row,Meter,Calibrator):
    
    Params= [row.PV,row.PU,row.PP,row.SV,row.SU,row.SP,row.FV,row.FU,row.FP]
    TP = TestPoint(Params)
    
    Calibrator.SetRange(TP,row['CalibratorFunction'])

    if row['CalibratorCommands']:
        Calibrator.SetCommands(row['CalibratorCommands'])
    
    Meter.SetRange(TP,row['MeterFunction'])
    
    Calibrator.Operate()

    Meter.TakeReading()

    Reads=3
    Readings=[]

    for n in range(Reads):
        Readings.append(Meter.TakeReading())

    Reading = sum(Readings)/len(Readings)

    Reading = Meter.TakeReading()
    
    if float(row['Tolerance_High']) >= TP.BuildFromPrimary(Reading) >= float(row['Tolerance_Low']):
        print ('Pass: ',TP.BuildFromPrimary(Reading))
        row['Disposition']='True'
        row['Reading']=TP.BuildFromPrimary(Reading)
    else:
        print ('Fail: ',TP.BuildFromPrimary(Reading))
        row['Disposition']='False'
        row['Reading']=TP.BuildFromPrimary(Reading)
        ms.Update('Warning, Detected OOT at Test Point: {0} {1} Readings: {2}'.format(row['Function'],row['Nominal'],TP.BuildFromPrimary(Reading)))
    
    time.sleep(2)

    return row
    
ms=slackmessenger()

df=pd.read_excel('TestPoints_Parsed_5522_.xlsx')
df = df.fillna('')

#Group = 'DC Voltage Normal'
#Group = 'AC Voltage'
#Group = 'DC AUX Voltage'
#Group = 'AC AUX Voltage'
#Group = 'DC Low Current'
#Group = 'DC High Current'
#Group = 'Resistance Low'
#Group = 'Resistance High'
#Group = 'Phase'
#Group = 'Phase High'
#Group = 'DC Current 329 uA'
#Group = 'DC Current 3.3 mA'
#Group = 'DC Current 33 mA'
#Group = 'DC Current 330 mA'
#Group = 'DC Current 3.3 A'
#Group = 'DC Current 20 A'


#Group = 'AC Current 330 uA Range'
#Group = 'AC Current 3.3 mA Range'
#Group = 'AC Current 33 mA Range'
#Group = 'AC Current 330 mA Range'

Group = 'High Capacitance'

df2 = SelectGroup(df,Group)

print (df2)

ms.Update('Starting Automation Test Point Group: {0}'.format(Group))
ms.Update('Group Consists of {0} test points'.format(df2.shape[0]))

try:
    #Meter = T8081('COM3')
    Meter = F8508('1')
    #Meter = F5790('2')
    #Meter = K53220A()
    #Calibrator = F5730A('COM5')
    #Calibrator = F5522A('COM6')

    if Group == 'High Capacitance':
        Standard = F5730A('COM3')
        Calibrator = F5522A('COM6')

        df2=df2.apply(Calibrate_Capacitance,args=(Standard,Calibrator),axis=1)

        Standard.disconnect()
        Calibrator.disconnect()

    else:

        #df2=df2.apply(Calibrate,args=(Meter,Calibrator),axis=1)

        #1000 Ohm Resistor
        #df2=df2.apply(Calibrate_OhmsLaw,args=(Meter,Calibrator,1000.0212),axis=1)

        #100 Ohm Resistor
        #df2=df2.apply(Calibrate_OhmsLaw,args=(Meter,Calibrator,100.0002),axis=1)

        #10 Ohm Resistor
        #df2=df2.apply(Calibrate_OhmsLaw,args=(Meter,Calibrator,10.000085),axis=1)

        #1 Ohm Resistor
        #df2=df2.apply(Calibrate_OhmsLaw,args=(Meter,Calibrator,0.999985),axis=1)

        #0.1 Ohm Resistor
        #df2=df2.apply(Calibrate_OhmsLaw,args=(Meter,Calibrator,0.09998097),axis=1)

        #0.01 Ohm Resistor
        #df2=df2.apply(Calibrate_OhmsLaw,args=(Meter,Calibrator,0.01000744),axis=1)

        Calibrator.Standby()
        
        Meter.disconnect()
        Calibrator.disconnect()

    df2.to_excel('5522_Data\\Readings_5522_{0}.xlsx'.format(Group))

    ms.Update('Conclusion of Automation Test Point Group: {0}'.format(Group))

except Exception as e:
    
    #exception handling code
    print(traceback.format_exc())
    Meter.disconnect()
    Calibrator.disconnect()
    
print ("Done")
