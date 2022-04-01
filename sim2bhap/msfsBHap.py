from time import sleep
from simconnect import SimConnect, PERIOD_VISUAL_FRAME
#import better_haptic_player as player
import haptic_player
import os
import time
import math
import traceback

varList = ["GENERAL ENG PCT MAX RPM:1", "AIRSPEED MACH", "BARBER POLE MACH",
           "ACCELERATION BODY X", "ACCELERATION BODY Y", "ACCELERATION BODY Z", 
           "TRAILING EDGE FLAPS LEFT PERCENT", "GEAR LEFT POSITION", "G FORCE"]

class Sim():
  def __init__(self, port = 500, ipAddr = '127.0.0.1'):
    self.speedThreshold = 0.75
    self.rpmThreshold = 0.95
    self.gfeThreshold = 3
    self.fullArms = False
    self.accelThreshold = 0.5
    self.player = haptic_player.HapticPlayer()
    
  def play(self, name, intensity, altname):
    self.player.submit_registered_with_option(name, altname,
       scale_option={"intensity": intensity, "duration": 1},
       rotation_option={"offsetAngleX": 0, "offsetY": 0})

  def start(self):
    self.cycle = 0
    self.ValueDict = {}
    self.sc = None
    self.lastAcel = None
    self.lastFlapPos = None
    self.lastGearPos = None
    errCode = 'valid'
    try:
      #player.initialize()
      
      # tact file can be exported from bhaptics designer
      self.player.register("msfs_vvne", "msfs_vvne.tact")
      self.player.register("msfs_vrpm", "msfs_vrpm.tact")
      self.player.register("msfs_vgfe", "msfs_vgfe.tact")
      self.player.register("msfs_arpm", "msfs_arpm.tact")
      self.player.register("msfs_vace", "msfs_vace.tact")
      self.player.register("msfs_vfla", "msfs_vfla.tact")
      # open a connection to the SDK
      # or use as a context via `with SimConnect() as sc: ... `
      self.sc = SimConnect()
      
      
      # subscribing to one or more variables is much more efficient,
      # with the SDK sending updated values up to once per simulator frame.
      # the variables are tracked in `datadef.simdata`
      # which is a dictionary that tracks the last modified time
      # of each variable.  changes can also trigger an optional callback function
      self.datadef = self.sc.subscribe_simdata(
          varList,
          # request an update every ten rendered frames
          period=PERIOD_VISUAL_FRAME,
          interval=1,
      )
      # track the most recent data update
      #self.latest = self.datadef.simdata.latest()
      #print("Inferred variable units", self.datadef.get_units())
      msg = "msfsBHap started\n"
    except Exception as excp:
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())
    return (msg, errCode)

  def runCycle(self):
    self.cycle += 1
    errCode = 'none'
    msg = ''
    try:
   
      # pump the SDK event queue to deal with any recent messages
      while self.sc.receive():
          pass
          
      #print (self.datadef.simdata)
   
      # show data that's been changed since the last update
      #print(f"Updated data {self.datadef.simdata.changedsince(self.latest)}")
      
      for varName in self.datadef.simdata:
        self.ValueDict[varName] = self.datadef.simdata[varName]

      impactForce = 0
      acelX = self.datadef.simdata["ACCELERATION BODY X"]
      acelZ = self.datadef.simdata["ACCELERATION BODY Z"]
      acel2 = math.sqrt(abs(acelX*acelZ))
      acelY = self.datadef.simdata["ACCELERATION BODY Y"]
      acel = math.sqrt(abs(acelY*acel2))
      if (self.lastAcel is not None):
        acelChange = abs(acel - self.lastAcel)
        impactForce = (acelChange - self.accelThreshold) / 50.0
      self.lastAcel = acel
      
      if impactForce > 0.1:
        msg += "Ace {} {}\n".format(impactForce, acelChange)
        self.play("msfs_arpm", impactForce, "alt1") 
        self.play("msfs_vace", impactForce, "alt2") 

      if self.cycle % 3 != 0:
        return (msg, errCode)
   
      #self.latest = self.datadef.simdata.latest()
   
      speedVibration = (self.datadef.simdata["AIRSPEED MACH"]/self.datadef.simdata["BARBER POLE MACH"]) - self.speedThreshold
      if (speedVibration > 0):
        speedVibration = speedVibration * speedVibration * 4
        if (speedVibration > 0.01):
          msg += "SPEED {} {}\n".format(speedVibration, self.datadef.simdata["AIRSPEED MACH"])
          if self.fullArms:
            self.play("msfs_arpm", speedVibration, "alt3")
          self.play("msfs_vvne", speedVibration, "alt4")
                      
      engineVibration = self.datadef.simdata["GENERAL ENG PCT MAX RPM:1"]/100 - self.rpmThreshold
      if (engineVibration > 0):
        engineVibration = engineVibration * engineVibration * 4
        if (engineVibration > 0.01):
          msg += "RPM {} {}\n".format(engineVibration, self.datadef.simdata["GENERAL ENG PCT MAX RPM:1"])
          self.play("msfs_arpm", engineVibration, "alt5")
          self.play("msfs_vrpm", engineVibration, "alt6")
   
      gForceVibration = (self.datadef.simdata["G FORCE"] - self.gfeThreshold) / 8
      if (gForceVibration > 0):
        gForceVibration = gForceVibration * gForceVibration * 4
        if (gForceVibration > 0.01):
          msg += "GFe {} {}\n".format(gForceVibration, self.datadef.simdata["G FORCE"])
          if self.fullArms:
            self.play("msfs_arpm", gForceVibration, "alt7")
          self.play("msfs_vgfe", gForceVibration, "alt8")

      flapsChange = 0
      flapPos = self.datadef.simdata["TRAILING EDGE FLAPS LEFT PERCENT"]
      if (self.lastFlapPos is not None):
        flapsChange = abs(flapPos - self.lastFlapPos)
      self.lastFlapPos = flapPos

      gearChange  = 0
      gearPos = self.datadef.simdata["GEAR LEFT POSITION"]
      if (self.lastGearPos is not None):
        gearChange = abs(gearPos - self.lastGearPos)
        print(gearChange)
      self.lastGearPos = gearPos
      
      if (flapsChange > 0.005) or (gearChange > 0.005):
        msg += "Flp {} {} {} {}\n".format(flapsChange, flapPos, gearChange, gearPos)
        if self.fullArms:
          self.play("msfs_arpm", 0.1, "alt9") 
        self.play("msfs_vfla", 0.5, "alt10") 

    except Exception as excp:
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())

    return (msg, errCode)
  def stop(self):
    #player.destroy()
    if self.sc:
      self.sc.Close()
      self.sc = None
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
