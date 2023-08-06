class valve():
    def __init__(self,name, motorDriver, motorChannel, RunDuration = 30, StartState = False):
        self.name = name
        self.state = StartState
        self.motorDriver = motorDriver
        self.motorChannel = motorChannel
        self.RunDuration = RunDuration
        
    def getState(self):
        return self.state
    
    def toggleState(self):
        self.state = not self.state
        return self.state
    
    def setState(self, state):
        self.state = state
    
    def getName(self):
        return self.name