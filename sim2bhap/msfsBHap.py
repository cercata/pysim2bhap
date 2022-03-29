from time import sleep
from simconnect import SimConnect, PERIOD_VISUAL_FRAME
import better_haptic_player as player
import os
import traceback

varList = ["GENERAL ENG RPM:1", "GENERAL ENG PCT MAX RPM:1", "PROP MAX RPM PERCENT:1", "AIRSPEED MACH", "BARBER POLE MACH",
           "ACCELERATION BODY X", "ACCELERATION BODY Y", "ACCELERATION BODY Z", "SIM ON GROUND", "TRAILING EDGE FLAPS LEFT PERCENT",
           "LEFT WHEEL RPM", "GEAR LEFT POSITION", "GEAR RIGHT POSITION", "G FORCE", "TITLE"]


class Sim():
  def __init__(self, port = 500, ipAddr = '127.0.0.1'):
    self.speedThreshold = 0.75
    self.rpmThreshold = 0.95
    self.gfThreshold = 3

  def start(self):
    self.cycle = 0
    self.ValueDict = {}
    self.sc = None
    errCode = 'valid'
    try:
      player.initialize()
      
      # tact file can be exported from bhaptics designer
      player.register("msfs_vvne", "msfs_vvne.tact")
      player.register("msfs_vrpm", "msfs_vrpm.tact")
      player.register("msfs_vgfe", "msfs_vgfe.tact")
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
      self.latest = self.datadef.simdata.latest()
      print("Inferred variable units", self.datadef.get_units())
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
   
      self.latest = self.datadef.simdata.latest()
   
      speedVibration = (self.datadef.simdata["AIRSPEED MACH"]/self.datadef.simdata["BARBER POLE MACH"]) - self.speedThreshold
      if (speedVibration > 0):
        speedVibration = speedVibration * speedVibration * 4
        if (speedVibration > 0.01):
          msg += "SPEED {} {}\n".format(speedVibration, self.datadef.simdata["AIRSPEED MACH"])
          player.submit_registered_with_option("msfs_vvne", "alt",
                        scale_option={"intensity": speedVibration, "duration": 1},
                        rotation_option={"offsetAngleX": 0, "offsetY": 0})
                      
      engineVibration = self.datadef.simdata["GENERAL ENG PCT MAX RPM:1"]/100 - self.rpmThreshold
      if (engineVibration > 0):
        engineVibration = engineVibration * engineVibration * 4
        if (engineVibration > 0.01):
          msg += "RPM {} {}\n".format(engineVibration, self.datadef.simdata["GENERAL ENG PCT MAX RPM:1"])
          player.submit_registered_with_option("msfs_vrpm", "alt2",
                        scale_option={"intensity": engineVibration, "duration": 1},
                        rotation_option={"offsetAngleX": 0, "offsetY": 0})
   
   
      gForceVibration = (self.datadef.simdata["G FORCE"] - self.gfThreshold) / 10
      if (gForceVibration > 0):
        gForceVibration = gForceVibration * gForceVibration * 4
        if (gForceVibration > 0.01):
          msg += "GFe {} {}\n".format(gForceVibration, self.datadef.simdata["G FORCE"])
          player.submit_registered_with_option("msfs_vgfe", "alt3",
                        scale_option={"intensity": gForceVibration, "duration": 1},
                        rotation_option={"offsetAngleX": 0, "offsetY": 0})
    except Exception as excp:
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())

    return (msg, errCode)
  def stop(self):
    if self.sc:
      self.sc.Close()
    player.destroy()
    return ("msfsBHap stopped\n", "valid")

if __name__ == "__main__": 

  sim = Sim()
  print(sim.start())
  sleep(3)
  while True:
    print(sim.runCycle())
    sleep(0.125)
  sim.stop()
