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
import re

refloatList = re.compile("-?\d+\.\d+")

class Sim(baseBHap.BaseSim):
  def __init__(self, port = 29373, ipAddr = '127.0.0.1'):
    self.s = None
    self.lastPacket = 0
    self.simTime = None
    self.acc = None
    self.shells = None
    baseBHap.BaseSim.__init__(self, port, ipAddr)
    
    
  def parseTelem(self, floatList):
    self.prevSimTime = self.simTime
    self.simTime = float(floatList[27])
    self.prevAcc = self.acc
    self.acc = [float(floatList[0])*9.8, float(floatList[1])*9.8, float(floatList[2])*9.8]
    accel2 = math.sqrt(self.acc[0]*self.acc[0]+self.acc[1]*self.acc[1])
    accel = math.sqrt(self.acc[2]*self.acc[2]+accel2*accel2)
    if (self.prevAcc is not None):
      prevAccel2 = math.sqrt(self.prevAcc[0]*self.prevAcc[0]+self.prevAcc[1]*self.prevAcc[1])
      prevAccel = math.sqrt(self.prevAcc[2]*self.prevAcc[2]+prevAccel2*prevAccel2)
      if self.simTime > self.prevSimTime:
        self.accelChange = abs(accel - prevAccel) / ((self.simTime - self.prevSimTime) * 50)
      else:
        self.accelChange = 0.0
        
    self.prevShells = self.shells
    self.shells = float(floatList[24])
    if (self.prevShells is not None):
      if self.shells < self.prevShells:
        self.cannon = 1
      
    self.rpmPerc = float(floatList[25]) / 100.0
    self.alt = float(floatList[17])
    self.gear = float(floatList[18])
    sum([float(floatList[13]), float(floatList[15]), float(floatList[16])])
    self.onGround = sum([float(floatList[13]), float(floatList[15]), float(floatList[16])]) > 0.01
    self.speed = float(floatList[23]) * 3.6
    self.aoa = float(floatList[22]) #* baseBHap.rad2Deg
    self.flaps = float(floatList[18])
    self.g = accel / 9.8
  
  def recvData(self):

    while True:
      try:
         (msg, addr) = self.s.recvfrom(10000)
         self.lastPacket = time.time()
         floatList = refloatList.findall(msg.decode('ascii'))
         self.parseTelem(floatList)

      except socket.error as e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            return
        else:
            # a "real" error occurred
            log.exception('')

  def start(self):
    self.s = None
    self.motionTick = None
    self.acc = None
    self.lastAccel = None

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
      
      msg = "DCSBHap started\n"
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
    return ("DCSBHap stopped\n", "valid")

if __name__ == "__main__": 

  sim = Sim()
  print(sim.start())
  while True:
    print(sim.runCycle())
    time.sleep(0.042)
  sim.stop()
