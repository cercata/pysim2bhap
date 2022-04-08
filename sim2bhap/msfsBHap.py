from time import sleep
#from importlib import reload 
#import better_haptic_player as player
import haptic_player
import os, sys
import time
import math
import traceback
import simconnect
import logging as log
import baseBHap


varList = ["GENERAL ENG PCT MAX RPM:1", "AIRSPEED MACH", "BARBER POLE MACH",
           "ACCELERATION BODY X", "ACCELERATION BODY Y", "ACCELERATION BODY Z", 
           "TRAILING EDGE FLAPS LEFT PERCENT", "GEAR LEFT POSITION", "G FORCE",
           "SIM ON GROUND", "INCIDENCE ALPHA", "INCIDENCE BETA"]

class Sim(baseBHap.BaseSim):
  def __init__(self, port = 500, ipAddr = '127.0.0.1'):
    baseBHap.BaseSim.__init__(self, port, ipAddr)
    
  def recvData(self):
    # pump the SDK event queue to deal with any recent messages
    while self.sc.receive():
        pass
        
    #for varName in self.datadef.simdata:
    #  self.ValueDict[varName] = self.datadef.simdata[varName]

    # show data that's been changed since the last update
    #print(f"Updated data {self.datadef.simdata.changedsince(self.latest)}")
    self.latest = self.datadef.simdata.latest()
    if self.latest:
      self.lastPacket = time.time()
    
    impactForce = 0
    acelX = self.datadef.simdata["ACCELERATION BODY X"]
    acelZ = self.datadef.simdata["ACCELERATION BODY Z"]
    acel2 = math.sqrt(acelX*acelX+acelZ*acelZ)
    acelY = self.datadef.simdata["ACCELERATION BODY Y"]
    acel = math.sqrt(acelY*acelY+acel2*acel2) * 0.3048
    if (self.lastAcel is not None):
      self.accelChange = abs(acel - self.lastAcel)
    self.lastAcel = acel
    
    self.onGround = self.datadef.simdata["SIM ON GROUND"]
    self.aoa = self.datadef.simdata["INCIDENCE ALPHA"] * baseBHap.rad2Deg
    self.speedPerc = self.datadef.simdata["AIRSPEED MACH"]/self.datadef.simdata["BARBER POLE MACH"]
    self.rpmPerc = self.datadef.simdata["GENERAL ENG PCT MAX RPM:1"]/100
    self.g = self.datadef.simdata["G FORCE"]
    self.flaps = self.datadef.simdata["TRAILING EDGE FLAPS LEFT PERCENT"]
    self.gear = self.datadef.simdata["GEAR LEFT POSITION"]
  
  def start(self):
    self.ValueDict = {}
    self.sc = None
    self.lastAcel = None
    errCode = 'valid'
    try:
      try:
        baseBHap.BaseSim.start(self)
      except:
        msg = 'Error conecting. Is bHaptics player app running?\n'
        log.exception(msg)
        return (msg, 'error')
      
      # open a connection to the SDK
      # or use as a context via `with SimConnect() as sc: ... `
      self.sc = simconnect.SimConnect(poll_interval_seconds=0.042)
      
      
      # subscribing to one or more variables is much more efficient,
      # with the SDK sending updated values up to once per simulator frame.
      # the variables are tracked in `datadef.simdata`
      # which is a dictionary that tracks the last modified time
      # of each variable.  changes can also trigger an optional callback function
      self.datadef = self.sc.subscribe_simdata(
          varList,
          # request an update every ten rendered frames
          period=simconnect.PERIOD_VISUAL_FRAME,
          interval=1,
      )
      # track the most recent data update
      #print("Inferred variable units", self.datadef.get_units())
      msg = "msfsBHap started\n"
    except Exception as excp:
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())
    return (msg, errCode)
  
  def stop(self):
    baseBHap.BaseSim.stop(self)
    if self.sc:
      self.sc.Close()
      self.sc = None
      del self.sc
      self.datadef = None
    return ("msfsBHap stopped\n", "valid")

if __name__ == "__main__": 

  sim = Sim()
  print(sim.start())
  sleep(3)
  while True:
    print(sim.runCycle())
    sleep(0.125)
  sim.stop()
