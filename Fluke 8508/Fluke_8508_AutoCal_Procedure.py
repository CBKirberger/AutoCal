# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 10:07:00 2020

This procedure is for the calibration of Fluke 8508 DMMs

Required Equipment
- Fluke 5730A
- Fluke 5725A
- Measurement International 10 GOhm Resistor
- Measurement International 1 GOhm Resistor
"""

from F8508 import F8508
from F5730A import F5730A
import master
import pandas as pd

########################################
# In the future use a WO number to autogenerate the test points. Cross reference
# the datasheet from the new WO with another parsed datasheet to determine if
# they are using a different revision/datasheet. If they are the user will have
# to manually make sure the test points have been correctly parsed.

TestPoints = pd.read_excel('TestPoints_Parsed_F8508.xlsx')

GroupNames = TestPoints.Group.unique()
if pd.isnull(GroupNames).any():
    print('WARNING: At least one test point has not been assigned a testing group.\n')


############################################
# Open Instruments
'''
Fluke8508 = F8508()
Fluke5730 = F5730A()
'''

###############################################
# Below here the actual calibration takes place
###############################################


print('Please choose a test point group from the following options by typing in the group name or corresponding number.')
Gnum = 1
for G in GroupNames:
    if not pd.isnull(G):
        print(str(Gnum) + '. ' + str(G))
        Gnum += 1

Group = input('Selection: ')
        
print('You have selected the group ' + str(Group) + '. Please ensure that your equipment is connected as shown in Figure 1.\n')\
# TODO: Add a display window which pops up with images of the lead connections, setup, all that jazz

Gotime = input('When you are ready to start taking data type "Start" and press enter: ')
while Gotime != 'Start':
    print('Invalid Input')
    Gotime = input('When you are ready to start taking data type "Start" and press enter: ')
    




