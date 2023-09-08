import time
import valve


MaximumWateringTime_ms = 30000

class valveSupervisor():
    def __init__(self,valveList):
        self.valveList         = valveList
        self.AutoWateringState = len(self.valveList)


    def StartAutoWatering(self):
        for valve in self.valveList:
            valve.setState(False)
        self.AutoWateringState = 0
        
    def StopAutoWatering(self):
        for valve in self.valveList:
            valve.setState(False)
        self.AutoWateringState = len(self.valveList)
        
    def GetAutoWatering(self):
        if self.AutoWateringState == len(self.valveList):
            return False
        else:
            return True
        

            

    
    def Tick(self):
        
        #check if the Auto watering is enabled, and the valve list is longer then 0
        if len(self.valveList) > self.AutoWateringState:
            
            #check if any valve is active:
            anyValveActive = False
            for valve in self.valveList:
                if valve.getState() == True:
                    anyValveActive = True
            
            if anyValveActive == False:
                self.valveList[self.AutoWateringState].setState(True)
                print('auto watering turn on valve '+ self.valveList[self.AutoWateringState].getName())
                self.AutoWateringState += 1
        
        

            
            