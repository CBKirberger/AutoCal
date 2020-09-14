import re
#from slack import WebClient
#from slack.errors import SlackApiError



class TestPoint():
    
    def __init__(self,Value):
        
        if type(Value)==str:
            self.BuildByString(Value)
        else:
            self.BuildByList(Value)
    
    def BuildByList(self,Value):
        
        self.PrimaryValue=Value[0]
        self.PrimaryUnit=Value[1]
        self.PrimaryPrefix=Value[2]
        
        self.SecondaryValue=Value[3]
        self.SecondaryUnit=Value[4]
        self.SecondaryPrefix=Value[5]

        self.FrequencyValue=Value[6]
        self.FrequencyUnit=Value[7]
        self.FrequencyPrefix=Value[8]
            
    def BuildByString(self,Value):
        
        if '@' in Value:
            
            amplitude=Value.split('~@')[0].rstrip(' ').lstrip(' ')
            frequency=Value.split('~@')[1].rstrip(' ').lstrip(' ')
            
            PrimaryUnit=re.findall('\S*$',amplitude)[0]
            
            self.PrimaryValue=re.findall('^[-]?\d*\.?\d*',amplitude)[0]
            self.PrimaryUnit,self.PrimaryPrefix=self.GetUnit(PrimaryUnit)
            
            SecondaryUnit=re.findall('\S*$',frequency)[0]
            
            self.FrequencyValue=re.findall('^[-]?\d*\.?\d*',frequency)[0]
            self.FrequencyUnit,self.FrequencyPrefix=self.GetUnit(SecondaryUnit)

            self.SecondaryValue=''
            self.SecondaryUnit=''
            self.SecondaryPrefix=''
            
        else:
            self.PrimaryValue=re.findall('^[-]?\d*\.?\d*',Value)[0]
            PrimaryUnit=re.findall('\S*$',Value)[0]
            self.PrimaryUnit,self.PrimaryPrefix=self.GetUnit(PrimaryUnit)

            self.SecondaryValue=''
            self.SecondaryUnit=''
            self.SecondaryPrefix=''

            self.FrequencyValue=''
            self.FrequencyUnit=''
            self.FrequencyPrefix=''
            
    def GetUnit(self,value):

        search = re.search('^\s*?(?P<prefix>G|T|M|k|m|u|µ)?(?P<unit>.*)$', value)
        return search.group('unit'),search.group('prefix')
    
    def getPrefixMultiplier(self,prefix):
        
        if not prefix:
            return 1
        
        if prefix == 'm':
            return 1e-3
        elif prefix == 'µ':
            return 1e-6
        elif prefix == 'k':
            return 1e3
        elif prefix == 'M':
            return 1e6
        elif prefix == 'G':
            return 1e9
        elif prefix == 'T':
            return 1e12
        
    def ComputeValue(self,Type='Primary'):
        
        if Type == 'Primary':
            return float(self.PrimaryValue)*float(self.getPrefixMultiplier(self.PrimaryPrefix))
        elif Type == 'Secondary':
            return float(self.SecondaryValue)*float(self.getPrefixMultiplier(self.SecondaryPrefix))
        elif Type == 'Frequency':
            print ("Here")
            print (self.FrequencyValue,self.FrequencyPrefix)
            print (self.getPrefixMultiplier(self.FrequencyPrefix))
            return (float(self.FrequencyValue)*float(self.getPrefixMultiplier(self.FrequencyPrefix)))
        
    
    def toList(self):
        
        return (self.PrimaryValue,self.PrimaryUnit,self.PrimaryPrefix,
        self.SecondaryValue,self.SecondaryUnit,self.SecondaryPrefix,
        self.FrequencyValue,self.FrequencyUnit,self.FrequencyPrefix)
        
    def BuildFromPrimary(self,number):
        
        return number/self.getPrefixMultiplier(self.PrimaryPrefix)
    
class Range():
    
    def __init__(self,Name,PU,PLowLimit,PHighLimit,SU,SLowLimit,SHighLimit,FunctionCommand=''):
        self.Name=Name
        self.PrimaryLowLimit=PLowLimit
        self.PrimaryHighLimit=PHighLimit
        self.PU=PU
        self.SU=SU
        self.SecondaryLowLimit=SLowLimit
        self.SecondaryHighLimit=SHighLimit
        self.FunctionCommand=FunctionCommand

    def ResolveTestPoint(self,TP):
        
        if TP.PrimaryUnit == self.PU and TP.SecondaryUnit == self.SU and abs(TP.ComputeValue(True)) >= self.LowLimit and abs(TP.ComputeValue(True)) <= self.HighLimit:
            return True,self.Name
        else:
            return False,''
        
    def getName(self):
        return self.Name
    
    def CompileCommand(self,TP):
        
        commands=self.FunctionCommand
        output_commands=[]
        
        for command in commands.split('|'):

            if '{PU}' in command:
                command=command.replace('{PU}',TP.PrimaryUnit)
            if '{SU}' in command:
                command=command.replace('{SU}',TP.SecondaryUnit)
            if '{FU}' in command:
                command=command.replace('{FU}',TP.FrequencyUnit)
            if '{PV}' in command:
                command=command.replace('{PV}',str(TP.ComputeValue('Primary')))
            if '{SV}' in command:
                command=command.replace('{SV}',str(TP.ComputeValue('Secondary')))
            if '{FV}' in command:
                command=command.replace('{FV}',str(TP.ComputeValue('Frequency')))
            
            output_commands.append(command)
            
        return output_commands

'''
class slackmessenger:

    def __init__(self):
        self.sc=WebClient(token="xoxb-496235538818-643271972822-XlTJysf19mUvVJ2NtXSZ4thk")

    def Update(self,message):
        self.sc.chat_postMessage(
            channel="#automation-updates",
            text=message
        )
        '''