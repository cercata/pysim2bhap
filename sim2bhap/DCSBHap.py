import socket
import time
import errno
import os
import time
import math
import traceback
import logging as log
import baseBHap
import re
import struct

refloatList = re.compile("-?\d+\.\d+")
structDR2   = struct.Struct("<"+"f"*66)

class Sim(baseBHap.BaseSim):
  def __init__(self, port = 29373, ipAddr = '127.0.0.1', simName = 'DCS'):
    baseBHap.BaseSim.__init__(self, port, ipAddr)
    self.s = None
    self.simTime = None
    self.acc = None
    self.shells = None
    self.simNum = 1 if simName == 'DCS' else 0
    self.isCar = False if simName == 'DCS' else True
    
    
  def parseTelem(self, floatList):
    self.prevSimTime = self.simTime
    self.simTime = float(floatList[27]) if self.simNum else floatList[0]

    if self.simTime != self.prevSimTime:
      self.lastPacket = time.time()
    
    self.prevAcc = self.acc
    self.acc = [float(floatList[0])*9.8, float(floatList[1])*9.8, float(floatList[2])*9.8] if self.simNum else [float(floatList[34])*9.8, float(floatList[35])*9.8, 0.0]
    accel2 = math.sqrt(self.acc[0]*self.acc[0]+self.acc[1]*self.acc[1])
    accel = math.sqrt(self.acc[2]*self.acc[2]+accel2*accel2)
    if (self.prevAcc is not None):
      prevAccel2 = math.sqrt(self.prevAcc[0]*self.prevAcc[0]+self.prevAcc[1]*self.prevAcc[1])
      prevAccel = math.sqrt(self.prevAcc[2]*self.prevAcc[2]+prevAccel2*prevAccel2)
      if self.simTime > self.prevSimTime:
        self.accelChange = abs(accel - prevAccel) / ((self.simTime - self.prevSimTime) * 50)
      else:
        self.accelChange = 0.0
        
    if self.simNum:
      self.prevShells = self.shells
      self.shells = float(floatList[24])
      if (self.prevShells is not None):
        if self.shells < self.prevShells:
          self.cannon = 1
      self.alt = float(floatList[17])
      self.onGround = sum([float(floatList[13]), float(floatList[15]), float(floatList[16])]) > 0.01
      self.aoa = float(floatList[22]) #* baseBHap.rad2Deg
      self.flaps = float(floatList[18])
      self.g = accel / 9.8
    else:
      self.gLon = float(floatList[34])
      self.gLat = float(floatList[35])
      self.vlfw = float(floatList[23])
      self.vrfw = float(floatList[24])
      self.vlrw = float(floatList[21])
      self.vrrw = float(floatList[22])
      
    if self.simNum:
      self.rpmPerc = float(floatList[25]) / 100.0 
    else:
      self.rpmPerc = floatList[37]/floatList[63] if floatList[63] else 0.0
    self.gear = float(floatList[19]) if self.simNum else floatList[33]
    #sum([float(floatList[13]), float(floatList[15]), float(floatList[16])])
    self.speed = float(floatList[23]) * 3.6 if self.simNum else float(floatList[7])
  
  def recvData(self):

    numPackets = 0
    while True:
      try:
         (msg, addr) = self.s.recvfrom(10000)
         numPackets += 1

      except socket.error as e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
          if numPackets == 0:
            return
          else:
            numPackets == 0
            if self.simNum == 1:
              floatList = refloatList.findall(msg.decode('ascii'))
            else:
              floatList = structDR2.unpack(msg[0:264])
            self.parseTelem(floatList)
            return
        else:
            # a "real" error occurred
            log.exception('')

  def start(self):

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
      
      msg = self.simName+"BHap started\n"
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
    return (self.simName+"BHap stopped\n", "valid")

if __name__ == "__main__": 

  sim = Sim()
  print(sim.start())
  while True:
    print(sim.runCycle())
    time.sleep(0.042)
  sim.stop()
