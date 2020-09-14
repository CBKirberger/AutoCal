#Populate Data

import pandas as pd
import pyodbc
import re

import sys,os

sys.path.append(os.path.abspath((os.path.join(sys.path[0],'..','Utility Classes'))))

from master import TestPoint,Range

def ParseTP(row):
    
    TP=TestPoint(row['Nominal'])
    Params = TP.toList()
    
    row['PV']=Params[0]
    row['PU']=Params[1]
    row['PP']=Params[2]
    
    row['SV']=Params[3]
    row['SU']=Params[4]
    row['SP']=Params[5]
    
    row['FV']=Params[6]
    row['FU']=Params[7]
    row['FP']=Params[8]
    
    row['Group']=''
    row['MeterFunction']=''
    row['MeterCommands']=''
    row['CalibratorFunction']=''
    row['CalibratorCommands']=''
    
    return row

def GetData(online):
    
    if online:
        
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=CL-SQL;DATABASE=mudcats;UID=app_mudcats;PWD=MudCat$')

        TestNo = 2130047

        query = '''
                Select Mudcats_DS_TestPoints.TP_DUI,
                Text_Function as "Function",
                Text_Nominal as "Nominal",
                Meas_Tol_High as "Tolerance_High",
                Meas_Tol_Low as "Tolerance_Low"
                
                from Mudcats_DS__Calibration
                join Mudcats_DS_TestPoints
                on Mudcats_DS_TestPoints.DS_ID = Mudcats_DS__Calibration.DS_ID
                where DS_IsActive = 1
                and isHistory=0
                and TestNo like '{0}'
                and IsHeaderRow = 0
                and isPageBreak = 0
        '''.format(TestNo)

        return pd.read_sql(query,cnxn)
       
    else:
        return pd.read_excel('TestPoints.xlsx')

df = GetData(True)
df = df.apply(ParseTP,axis=1)
df.to_excel('TestPoints_Parsed_34401.xlsx')