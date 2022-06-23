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
from multiprocessing import shared_memory

structInt32    = struct.Struct("@"+"i")
structInt32_2  = struct.Struct("@"+"ii")
structFloat_3  = struct.Struct("@"+"f"*3)

structDouble   = struct.Struct("@"+"d")
structDouble_3 = struct.Struct("@"+"d"*3)
structDouble_4 = struct.Struct("@"+"d"*4)

class Sim(baseBHap.BaseSim):
  def __init__(self, port = 0, ipAddr = ''):
    baseBHap.BaseSim.__init__(self, port, ipAddr)
    self.s = None
    self.simTime = None
    self.acc = None
    self.shells = None
    self.isCar = True
    
    
  def parseTelem(self):
    buffer = self.shm.buf
  
    self.prevSimTime = self.simTime
    self.simTime, = structDouble.unpack(bytes(buffer[40:48]))

    if self.simTime != self.prevSimTime:
      self.lastPacket = time.time()
   
    #lveloc = structDouble_3.unpack(bytes(buffer[96:120]))
    #self.speed
    
    self.prevAcc = self.acc
    self.acc = structDouble_3.unpack(bytes(buffer[144:168]))
    accel2 = math.sqrt(self.acc[0]*self.acc[0]+self.acc[1]*self.acc[1])
    accel = math.sqrt(self.acc[2]*self.acc[2]+accel2*accel2)
    if (self.prevAcc is not None):
      prevAccel2 = math.sqrt(self.prevAcc[0]*self.prevAcc[0]+self.prevAcc[1]*self.prevAcc[1])
      prevAccel = math.sqrt(self.prevAcc[2]*self.prevAcc[2]+prevAccel2*prevAccel2)
      if self.simTime > self.prevSimTime:
        self.accelChange = abs(accel - prevAccel) / ((self.simTime - self.prevSimTime) * 50)
      else:
        self.accelChange = 0.0
    
    #gForce = structDouble_3.unpack(bytes(buffer[288:312]))
    
    self.susVel = structDouble_4.unpack(bytes(buffer[416:448]))
    
    rps, max_rps, urps = structFloat_3.unpack(bytes(buffer[1340:1352]))
    self.rpmPerc = rps / max_rps
    
    self.gear, = structInt32.unpack(bytes(buffer[1352:1356]))
  

  
  def recvData(self):

    self.parseTelem()

  def start(self):

    errCode = 'valid'
    try:
      try:
        self.shm = shared_memory.SharedMemory("$R3E")
      except FileNotFoundError:
        msg = 'Shared memory not available. Is Raceroom running?\n'
        log.exception(msg)
        return (msg, 'error')
      try:
        baseBHap.BaseSim.start(self)
      except:
        msg = 'Error conecting. Is bHaptics player app running?\n'
        log.exception(msg)
        return (msg, 'error')
      
      msg = "R3EBHap started\n"
    except Exception as excp:
      log.exception('')
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())
    return (msg, errCode)

  def stop(self):
    baseBHap.BaseSim.stop(self)
    return ("R3EBHap stopped\n", "valid")

if __name__ == "__main__": 

  sim = Sim()
  print(sim.start())
  while True:
    print(sim.runCycle())
    time.sleep(0.042)
  sim.stop()
