import time

StartState = False
DefaultValveRunTime_ms = 20000
DefaultValveBacklash_ms = 1000
DefaultValveBrakeTime_ms = 500
speed = 100

class valve():
    def __init__(self,name, motorChannel, motorboard, maxOnTime_ms = 30000):
        self.name              = name
        self.motorChannel      = motorChannel
        self.state             = StartState
        self.motorboard        = motorboard
        self.maxOnTime_ms	   = maxOnTime_ms
        self.ValveRunTime_ms   = DefaultValveRunTime_ms
        self.ValveBacklash_ms  = DefaultValveBacklash_ms
        self.ValveBrakeTime_ms = DefaultValveBrakeTime_ms
        self.LastChangeTime = time.ticks_ms() - self.maxOnTime_ms   # do this to prevent valve alignment during start-up
        
    def getState(self):
        return self.state
    
    def toggleState(self):
        return setState(not self.state)
    
    def setState(self, state):
        if state != self.state:
            self.state = state
            timestamp = time.ticks_ms()
            if timestamp - self.LastChangeTime < self.ValveBrakeTime_ms:
                # state was reverted before movement started, restore all defaults, and make sure no movement starts
                self.ValveRunTime_ms   = DefaultValveRunTime_ms
                self.ValveBacklash_ms  = DefaultValveBacklash_ms
                self.ValveBrakeTime_ms = DefaultValveBrakeTime_ms
                self.LastChangeTime    = timestamp - self.ValveBrakeTime_ms - self.ValveRunTime_ms - self.ValveBrakeTime_ms - self.ValveBacklash_ms
            elif timestamp - self.LastChangeTime  < self.ValveBrakeTime_ms + self.ValveRunTime_ms:
                #motor movement in progress, calculate path back!
                self.ValveRunTime_ms   = timestamp - self.LastChangeTime - self.ValveBrakeTime_ms + self.ValveBacklash_ms
                self.LastChangeTime    = timestamp
            elif timestamp - self.LastChangeTime  < self.ValveBrakeTime_ms + self.ValveRunTime_ms + self.ValveBrakeTime_ms:
                #motor was in the far end position, just before the backlash move
                self.ValveRunTime_ms   = DefaultValveRunTime_ms + DefaultValveBacklash_ms
                self.ValveBacklash_ms  = DefaultValveBacklash_ms
                self.ValveBrakeTime_ms = DefaultValveBrakeTime_ms
                self.LastChangeTime    = timestamp
            elif timestamp - self.LastChangeTime  < self.ValveBrakeTime_ms + self.ValveRunTime_ms + self.ValveBrakeTime_ms:
                #motor was busy with backlash move
                self.ValveRunTime_ms   = DefaultValveRunTime_ms + DefaultValveBacklash_ms## deze is nog niet goed omdat al iets van de baclash move gedaan was
                self.ValveBacklash_ms  = DefaultValveBacklash_ms
                self.ValveBrakeTime_ms = DefaultValveBrakeTime_ms
                self.LastChangeTime    = timestamp - self.ValveBrakeTime_ms # skip the first brake since we are moving in the correct direction
            else:
                self.ValveRunTime_ms   = DefaultValveRunTime_ms
                self.ValveBacklash_ms  = DefaultValveBacklash_ms
                self.ValveBrakeTime_ms = DefaultValveBrakeTime_ms
                self.LastChangeTime    = timestamp
            
        return state
        
    
    def getName(self):
        return self.name
    
    def getMotorChannel(self):
        return self.motorChannel
    
    def getActiveStateTime(self):
        return time.ticks_ms() - self.LastChangeTime
    
    def Tick(self):
        
        
        if self.getState() == True and self.getActiveStateTime() > self.maxOnTime_ms:
            self.setState(False)
            print('auto turn off valve '+self.getName())

        elif self.getActiveStateTime() < self.ValveBrakeTime_ms:
            self.motorboard.motorOff(self.getMotorChannel())
        elif self.getActiveStateTime() < self.ValveBrakeTime_ms + self.ValveRunTime_ms:
            #Valve is in transit
            if self.state == True:
                self.motorboard.motorOn(self.getMotorChannel(), 'f', speed)
            else:
                self.motorboard.motorOn(self.getMotorChannel(), 'r', speed)
        elif self.getActiveStateTime() < self.ValveBrakeTime_ms + self.ValveRunTime_ms + self.ValveBrakeTime_ms:
            #Valve is braking after transit
            self.motorboard.motorOff(self.getMotorChannel())
        elif self.getActiveStateTime() < self.ValveBrakeTime_ms + self.ValveRunTime_ms + self.ValveBrakeTime_ms + self.ValveBacklash_ms:
            if self.state == True:
                self.motorboard.motorOn(self.getMotorChannel(), 'r', speed)
            else:
                self.motorboard.motorOn(self.getMotorChannel(), 'f', speed)
        else:
            self.motorboard.motorOff(self.getMotorChannel())