import socket
import struct
import time
import errno
import haptic_player
import os
import time
import math
import traceback

structMotion  = struct.Struct("<Lfffffffff")
structTelem   = struct.Struct("<HLB")
structVarHead = struct.Struct("<HB")
structLong    = struct.Struct("<L")
structFloat1  = struct.Struct("<f")
structFloat2  = struct.Struct("<ff")
structFloat3  = struct.Struct("<fff")
structFloat4  = struct.Struct("<ffff")
structFloat = [None, structFloat1, structFloat2, structFloat3, structFloat4]


class Sim():
  def __init__(self, port = 29373, ipAddr = '127.0.0.1'):
    self.s = None
    self.port = port
    self.ipAddr = ipAddr
    self.speedThreshold = 0.75
    self.rpmThreshold = 0.95
    self.gfeThreshold = 2.6
    self.fullArms = False
    self.accelThreshold = 0.5
    self.maxSpeed = 700.0
    self.maxRpm = 3000.0
    self.forceMultiplier = 1.0
    self.player = haptic_player.HapticPlayer()
    
  def play(self, name, intensity, altname, duration = 1):
    self.player.submit_registered_with_option(name, altname,
       scale_option={"intensity": intensity*self.forceMultiplier, "duration": duration},
       rotation_option={"offsetAngleX": 0, "offsetY": 0})
  
  def parseMotion(self, buff):
    (motionTick, _, _, _, _, _, _, accX, accY, accZ) = structMotion.unpack(buff[0:40])
    self.prevMotionTick = self.motionTick
    self.motionTick = motionTick
    self.prevAcc = self.acc
    self.acc = [accX, accY, accZ]
    
  def parseTelem(self, buff):
    (packetLen, telemTick, numVars) = structTelem.unpack(buff[0:7])
    self.packetLen = packetLen
    self.telemTick = telemTick
    pos = 7
    for i in range(numVars):
      (varId, numFloats) = structVarHead.unpack(buff[pos:pos+3])
      pos += 3
      value = structFloat[numFloats].unpack(buff[pos:pos+numFloats*4])
      pos += numFloats*4
      if (varId == 0):
        self.rpm = max (value)
      elif (varId == 10):
        self.alt = value[0]
      elif (varId == 4):
        self.gear = sum(value)
      elif (varId == 6):
        self.speed = value[0]
      elif (varId == 8):
        g1 = math.sqrt(value[0]*value[0]+value[1]*value[1])
        g2 = math.sqrt(value[2]*value[2]+g1*g1)
        self.g = g2 / 9.8
        print (self.g)
      elif (varId == 11):
        self.flaps = value[0]
      print ("Var {} : {}".format(varId, value))
    lastByte = buff[pos]
    hitThreashold = 156
    self.gun = (lastByte == 1) and (packetLen < hitThreashold)
    self.cannon = (lastByte in (2,3)) and (packetLen < hitThreashold)
    self.hit = ((lastByte < 8) or (lastByte > 9)) and (packetLen >= hitThreashold)
    print ("Last Byte {}".format(lastByte))
  
  def recvUdpData(self):

    while True:
      try:
         (msg, addr) = self.s.recvfrom(10000)
         (packetID ,) = structLong.unpack(msg[0:4])
         if packetID == 0x494C0100:
           self.parseMotion(msg[4:])
         elif packetID == 0x54000101:
           self.parseTelem(msg[4:])
         else:
           return

      except socket.error as e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            return
        else:
            # a "real" error occurred
            print (e)

  def start(self):
    self.cycle = 0
    self.ValueDict = {}
    self.s = None
    self.motionTick = None
    self.acc = None
    self.lastAccel = None
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
      
      self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
      self.s.bind((self.ipAddr, self.port))
      self.s.setblocking(0)
      
      msg = "il2bBHap started\n"
    except Exception as excp:
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())
    return (msg, errCode)

  def runCycle(self):
    self.cycle += 1
    errCode = 'none'
    msg = ''
    try:
   
      self.recvUdpData()
      
      
      if self.acc is not None:
        impactForce = 0
        accel2 = math.sqrt(self.acc[0]*self.acc[0]+self.acc[1]*self.acc[1])
        accel = math.sqrt(self.acc[2]*self.acc[2]+accel2*accel2)
        if (self.prevAcc is not None):
          prevAccel2 = math.sqrt(self.prevAcc[0]*self.prevAcc[0]+self.prevAcc[1]*self.prevAcc[1])
          prevAccel = math.sqrt(self.prevAcc[2]*self.prevAcc[2]+prevAccel2*prevAccel2)
          if self.motionTick > self.prevMotionTick:
            accelChange = abs(accel - prevAccel) / (self.motionTick - self.prevMotionTick)
            impactForce = (accelChange - self.accelThreshold) / 20.0
        
        if impactForce >= 0.01:
          msg += "Acc {} {}\n".format(impactForce, accelChange)
          self.play("msfs_arpm", impactForce, "alt1") 
          self.play("msfs_vace", impactForce, "alt2") 
     
      if self.cycle % 3 != 0:
        return (msg, errCode)
   
   
      if hasattr(self, "speed"):
        speedVibration = (self.speed*3.6/self.maxSpeed) - self.speedThreshold
        if (speedVibration > 0):
          speedVibration = speedVibration * speedVibration * 8
          if (speedVibration > 0.01):
            msg += "SPEED {} {}\n".format(speedVibration, self.speed*3.6)
            if self.fullArms:
              self.play("msfs_arpm", speedVibration, "alt3")
            self.play("msfs_vvne", speedVibration, "alt4")
                      
      if hasattr(self, "rpm"):
        engineVibration = self.rpm/self.maxRpm - self.rpmThreshold
        if (engineVibration > 0):
          engineVibration = engineVibration * engineVibration * 16
          if (engineVibration > 0.01):
            msg += "RPM {} {}\n".format(engineVibration, self.rpm)
            self.play("msfs_arpm", engineVibration, "alt5")
            self.play("msfs_vrpm", engineVibration, "alt6")
   
      if hasattr(self, "g"):
        gForceVibration = (self.g - self.gfeThreshold) / 8
        if (gForceVibration > 0):
          gForceVibration = gForceVibration * gForceVibration * 4
          if (gForceVibration > 0.01):
            msg += "GFe {} {}\n".format(gForceVibration, self.g)
            if self.fullArms:
              self.play("msfs_arpm", gForceVibration, "alt7")
            self.play("msfs_vgfe", gForceVibration, "alt8")

      flapsChange = 0
      flapPos = None
      if hasattr(self, "flaps"):
        flapPos = self.flaps
        if (self.lastFlapPos is not None):
          flapsChange = abs(flapPos - self.lastFlapPos)
        self.lastFlapPos = flapPos

      gearChange  = 0
      gearPos = None
      if hasattr(self, "flaps"):
        gearPos = self.gear
        if (self.lastGearPos is not None):
          gearChange = abs(gearPos - self.lastGearPos)
        self.lastGearPos = gearPos
      
      if (flapsChange > 0.005) or (gearChange > 0.005):
        msg += "Flp {} {} {} {}\n".format(flapsChange, flapPos, gearChange, gearPos)
        if self.fullArms:
          self.play("msfs_arpm", 0.1, "alt9") 
        self.play("msfs_vfla", 0.3, "alt10")

      if hasattr(self, "gun"):
        if self.gun or self.cannon or self.hit:
          if self.hit:
            impactForce = 1.0
          elif self.cannon:
            impactForce = 0.5
          else:
            impactForce = 0.3
          msg += "hit {} {}\n".format(impactForce, accelChange)
          self.play("msfs_arpm", impactForce / 2, "alt1", 2) 
          self.play("msfs_vace", impactForce, "alt2", 2) 

    except Exception as excp:
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())

    return (msg, errCode)
  def stop(self):
    if self.s:
      self.s.close()
      self.s = None
    return ("il2bBHap stopped\n", "valid")

if __name__ == "__main__": 

  sim = Sim()
  print(sim.start())
  while True:
    print(sim.runCycle())
    time.sleep(0.042)
  sim.stop()