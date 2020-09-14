#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import time
import pymsgbox
import functools

#Change the System Path to the locations that contain the Modules
sys.path.append('../InstrumentClasses/')

#Import the Modules associated with the test equipment that will be used in the program
from F5730 import F5730
from F8508 import F8508
from datetime import datetime

#Importing the source. The source will operate on the applicable COM port. Check "Device Manager"
print ("Enter the COM port assigned to the Fluke 5730A. (example: 'COM3')")
Calibrator=F5730(raw_input())

#Importing the meter. Communications is through GPIB, therefore the address should not change.
Meter = F8508(1)

#Set the Calibrator's current value in terms of amp.
print ("Enter the mA DC Current value to source from the Fluke 5730A. (example: '0.8' for 800 µA )")
currentValue = float(raw_input()) / 1000

#Overload protection. User entries that exceed the maximum required current for testing will be denied.
while currentValue > 0.009:
    print("Error: Entry must be a mA value. Try again.")
    currentValue = float(raw_input()) / 1000

#Connect the Source and Meter
print ("Connecting to Calibrator....")
Calibrator.connect()
print ("\b....connected.")
print ("Connecting to Multimeter....")
Meter.connect()
print ("\b....connected.")

def DC_CurrentRange():
    print ("Testing Capacitance....")
    
    #Set 8508A to measure DC Voltage on 20 V range.
    Meter.setinputDCV(Range="19.0",resolution="RESL5",fast="FAST_ON")

    #Set 5730A to output DC Current.
    Calibrator.setOutput("A", currentValue)

    #Set Calibrator to OPERATE and begin taking measurements.
    print ("\b....now!")
    Calibrator.operate()
    tStamp1 = datetime.now()
    voltage1 = Meter.TakeReading(),
    tStamp2 = datetime.now()
    voltage1 = functools.reduce(lambda sub, ele: sub * 10 + ele, voltage1)
    print ("Initial Voltage = ", voltage1, "V")
    time.sleep(4.6665)
    tStamp3 = datetime.now()
    voltage2 = (Meter.TakeReading()),
    tStamp4 = datetime.now()
    Calibrator.standby()
    voltage2 = functools.reduce(lambda sub, ele: sub * 10 + ele, voltage2)
    print ("Final Voltage = ", voltage2, "V")
    
    #Calculates the time between voltage measurements
    tStampResult = (((tStamp4 - tStamp3) / 2) + (tStamp3 - tStamp2)+((tStamp2 - tStamp1) / 2))
    print ("Total Time = ", tStampResult.total_seconds(), "s")
    
    #Calculated Capacitance = CurrentSource x (DeltaTime / DeltaVoltage)
    calculatedCapacitance = float(currentValue) * (tStampResult.total_seconds()/(voltage2 - voltage1))
    
    #Displays calculated capacitance in terms of mF.
    print ("Calculated Capacitance = ", calculatedCapacitance * 1000, "mF")
    
    print ("Done.")

DC_CurrentRange()


# In[ ]:




