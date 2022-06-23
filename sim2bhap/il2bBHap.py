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
import baseBHap


structMotion  = struct.Struct("<Lfffffffff")
structTelem   = struct.Struct("<HLB")
structVarHead = struct.Struct("<HB")
structLong    = struct.Struct("<L")
structFloat1  = struct.Struct("<f")
structFloat2  = struct.Struct("<ff")
structFloat3  = struct.Struct("<fff")
structFloat4  = struct.Struct("<ffff")
structFloat = [None, structFloat1, structFloat2, structFloat3, structFloat4]

class Sim(baseBHap.BaseSim):
  def __init__(self, port = 29373, ipAddr = '127.0.0.1'):
    baseBHap.BaseSim.__init__(self, port, ipAddr)
    self.s = None
    self.motionTick = None
    self.acc = None
    
  def parseMotion(self, buff):
    (motionTick, _, _, _, _, _, _, accX, accY, accZ) = structMotion.unpack(buff[0:40])
    self.prevMotionTick = self.motionTick
    self.motionTick = motionTick
    self.prevAcc = self.acc
    self.acc = [accX, accY, accZ]
    accel2 = math.sqrt(self.acc[0]*self.acc[0]+self.acc[1]*self.acc[1])
    accel = math.sqrt(self.acc[2]*self.acc[2]+accel2*accel2)
    if (self.prevAcc is not None):
      prevAccel2 = math.sqrt(self.prevAcc[0]*self.prevAcc[0]+self.prevAcc[1]*self.prevAcc[1])
      prevAccel = math.sqrt(self.prevAcc[2]*self.prevAcc[2]+prevAccel2*prevAccel2)
      if self.motionTick > self.prevMotionTick:
        self.accelChange = abs(accel - prevAccel) / (self.motionTick - self.prevMotionTick)
    
  def parseTelem(self, buff):
    (packetLen, telemTick, numVars) = structTelem.unpack(buff[0:7])
    self.packetLen = packetLen
    self.telemTick = telemTick
    pos = 7
    self.onGround = 0
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
      elif (varId == 5):
        self.onGround = (value[0]+value[1]) > 0.01
      elif (varId == 6):
        self.speed = value[0] *3.6
      elif (varId == 7):
        self.aoa = value[0] * baseBHap.rad2Deg
      elif (varId == 8):
        g1 = math.sqrt(value[0]*value[0]+value[1]*value[1])
        g2 = math.sqrt(value[2]*value[2]+g1*g1)
        self.g = g2 / 9.8
      elif (varId == 11):
        self.flaps = value[0]
      #print ("Var {} : {}".format(varId, value))
    lastByte = buff[pos]
    if self.onGround:
      self.aoa = 0.0
    gunThreashold = 200
    hitThreashold = 500 #156
    self.gun |= (lastByte in (1,)) and (packetLen < gunThreashold)
    self.cannon |= (lastByte in (2, 3, 4, 5)) and (packetLen < gunThreashold)
    self.hit |= (lastByte not in (8, 9, 10, 11, 12, 13)) and (packetLen >= hitThreashold)
    if self.hit:
      print ("Hit {} len {}".format(lastByte, packetLen))
    #print ("Last Byte {}".format(lastByte))
  
  def recvData(self):

    while True:
      try:
         (msg, addr) = self.s.recvfrom(10000)
         self.lastPacket = time.time()
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
            log.exception('')

  def start(self):
    self.motionTick = None

    errCode = 'valid'
    try:
      try:
        baseBHap.BaseSim.start(self)
      except:
        msg = 'Error conecting. Is bHaptics player app running?\n'
        log.exception(msg)
        return (msg, 'error')
      
      self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
      self.s.bind((self.ipAddr, self.port))
      self.s.setblocking(0)
      
      msg = "il2bBHap started\n"
    except Exception as excp:
      log.exception('')
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())
    return (msg, errCode)

  def stop(self):
    baseBHap.BaseSim.stop(self)
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
