import socket
import struct
import time
import errno
import haptic_player
import os
import time
import math
import traceback
import logging as log

rad2Deg = 57.2958

class BaseSim():
  def __init__(self, port = 29373, ipAddr = '127.0.0.1'):
    self.port = port
    self.ipAddr = ipAddr
    self.lastPacket = 0
    self.speedThreshold = 0.75
    self.rpmThreshold = 0.95
    self.gfeThreshold = 2.6
    self.fullArms = False
    self.accelThreshold = 0.75
    self.maxSpeed = 700.0
    self.maxRpm = 3000.0
    self.aoaThreshold = 0.75
    self.maxAoA = 20
    self.forceMultiplier = 1.0
    self.durationMultiplier = 1.0
    self.ignoreFlaps = False
    self.fullArms = False
    self.player = haptic_player.HapticPlayer()
    
  def play(self, name, intensity, altname, duration = 1):
    self.player.submit_registered_with_option(name, altname,
       scale_option={"intensity": intensity*self.forceMultiplier, "duration": duration*self.durationMultiplier},
       rotation_option={"offsetAngleX": 0, "offsetY": 0})
  
  
  def recvData(self):
    raise Exception ('This was suppossed to be an abstract class')
    '''Must provide the follwing vars in the inherited class:
    self.accelChange
    self.rpm or self.rpmPerc
    self.alt (m)
    self.gear     = 1 - extended , 0 - retracted
    self.onGround = True if plane is on ground
    self.speed (kmh) or self.speedPerc
    self.aoa (deg)
    self.g (Gs)
    self.flaps  = 1 - extended , 0 - retracted
    self.gun    = True if firing (must be set to false in runCycle
    self.cannon = True if firing (must be set to false in runCycle
    self.hit    = True if impacted (must be set to false in runCycle
    '''
    
    
  def runCycle(self):
    raise Exception ('This was suppossed to be an abstract class')

  def start(self):
    self.cycle = 0
    self.lastFlapPos = None
    self.lastGearPos = None
    self.gun = 0
    self.cannon = 0
    self.hit = 0
      
    # tact file can be exported from bhaptics designer
    try:
      self.player = haptic_player.HapticPlayer()
      
      self.player.register("msfs_vvne", "msfs_vvne.tact")
      self.player.register("msfs_vrpm", "msfs_vrpm.tact")
      self.player.register("msfs_vgfe", "msfs_vgfe.tact")
      self.player.register("msfs_arpm", "msfs_arpm.tact")
      self.player.register("msfs_vace", "msfs_vace.tact")
      self.player.register("msfs_vfla", "msfs_vfla.tact")
      self.player.register("msfs_vaoa", "msfs_vaoa.tact")
    except:
      msg = 'Error conecting. Is bHaptics player app running?\n'
      log.exception(msg)
      raise
    

  def runCycle(self):
    self.cycle += 1
    errCode = 'none'
    msg = ''
    try:
   
      self.recvData()
      
      if (time.time() - self.lastPacket) > 0.5:
        msg = "No fresh telemetry data\n"
        return (msg, errCode)
      
      if hasattr(self, "accelChange"):
        impactForce = ((self.accelChange - self.accelThreshold) / 20.0) * 2 + 0.0099
        
        if impactForce >= 0.01:
          msg += "Acc {} {}\n".format(impactForce, self.accelChange)
          self.play("msfs_arpm", impactForce, "alt1") 
          self.play("msfs_vace", impactForce, "alt2") 
     
      if self.cycle % 3 != 0:
        return (msg, errCode)
   
   
      if hasattr(self, "aoa"):
        aoaVibration = ((self.aoa/self.maxAoA) - self.aoaThreshold) / (1 - self.aoaThreshold)
        if (aoaVibration > 0.01):
            msg += "AoA {} {}\n".format(aoaVibration, self.aoa)
            if self.fullArms:
              self.play("msfs_arpm", aoaVibration, "alt3")
            self.play("msfs_vaoa", aoaVibration, "alt4")
                      
      if hasattr(self, "speed"):
        self.speedPerc = self.speed/self.maxSpeed
      if hasattr(self, "speedPerc"):      
        speedVibration = (self.speedPerc - self.speedThreshold) / (1 - self.speedThreshold)
        if (speedVibration > 0.01):
          msg += "SPEED {} {}\n".format(speedVibration, self.speedPerc)
          if self.fullArms:
            self.play("msfs_arpm", speedVibration, "alt5")
          self.play("msfs_vvne", speedVibration, "alt6")
                      
      if hasattr(self, "rpm"):
        self.rpmPerc = self.rpm/self.maxRpm
      if hasattr(self, "rpmPerc"):
        if self.rpmPerc < 1.0:
          engineVibration = (self.rpmPerc - self.rpmThreshold) / ((1 - self.rpmThreshold) * 6)
        else:
          engineVibration = 1.0/6 + ((self.rpmPerc - 1.0) *1) / ((1 - self.rpmThreshold) * 2.5)
        if (engineVibration > 0.01):
          msg += "RPM {} {}\n".format(engineVibration, self.rpmPerc)
          self.play("msfs_arpm", engineVibration, "alt7")
          self.play("msfs_vrpm", engineVibration, "alt8")
   
      if hasattr(self, "g"):
        gForceVibration = (self.g - self.gfeThreshold) / 4
#        if (gForceVibration > 0):
#          gForceVibration = gForceVibration * 8
        if (gForceVibration > 0.01):
            msg += "GFe {} {}\n".format(gForceVibration, self.g)
            if self.fullArms:
              self.play("msfs_arpm", gForceVibration, "alt9")
            self.play("msfs_vgfe", gForceVibration, "alt10")

      flapsChange = 0
      flapPos = None
      
      if (not self.ignoreFlaps) and hasattr(self, "flaps"):
        flapPos = self.flaps
        if (self.lastFlapPos is not None):
          flapsChange = abs(flapPos - self.lastFlapPos)
        self.lastFlapPos = flapPos

      gearChange  = 0
      gearPos = None
      if hasattr(self, "gear"):
        gearPos = self.gear
        if (self.lastGearPos is not None):
          gearChange = abs(gearPos - self.lastGearPos)
        self.lastGearPos = gearPos
      
      if (flapsChange > 0.005) or (gearChange > 0.005):
        msg += "Flp {} {} {} {}\n".format(flapsChange, flapPos, gearChange, gearPos)
        if self.fullArms:
          self.play("msfs_arpm", 0.2, "alt11") 
        self.play("msfs_vfla", 0.5, "alt12")

      if self.gun or self.cannon or self.hit:
        if self.hit:
          impactForce = 1.0
        elif self.cannon:
          impactForce = 0.5
        else:
          impactForce = 0.3
        msg += "hit {}\n".format(impactForce)
        self.play("msfs_arpm", impactForce / 2, "alt13", 2) 
        self.play("msfs_vace", impactForce, "alt14", 2)
        self.gun = 0
        self.cannon = 0
        self.hit = 0

    except Exception as excp:
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())

    return (msg, errCode)
    
  def stop(self):
    pass

