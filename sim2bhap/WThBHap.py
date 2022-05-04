import time
import errno
import haptic_player
import os
import time
import math
import traceback
import logging as log
import baseBHap
import urllib.request
import json
import pygame

urls = 'http://{}:{}/state'
urli = 'http://{}:{}/indicators'
joyNumber = 1
joytrigger = 5

class Sim(baseBHap.BaseSim):
  def __init__(self, port = 8111, ipAddr = '127.0.0.1'):
    baseBHap.BaseSim.__init__(self, port, ipAddr)
    self.urls = urls.format(ipAddr, port)
    self.urli = urli.format(ipAddr, port)
    self.acc = None
    self.simTime = None
    self.triggerWorkaround = True

  def __del__(self):
    pass
    
    
  def parseTelem(self, varDict):
    if ('valid' in varDict) and (varDict['valid']):
      self.prevSimTime = self.simTime
      self.simTime = time.time()
    else:
      return
    self.prevAcc = self.acc
    
    
    if 'Ny' in varDict:
      self.g = varDict['Ny']
      self.acc = varDict['Ny']*9.8
      if (self.prevAcc is not None):
        self.accelChange = abs(self.acc - self.prevAcc) / ((self.simTime - self.prevSimTime) * 50)
       
    # "type": "f4u-1c",    
    if "weapon1" in varDict:
      if varDict["weapon1"]:
        self.gun = 1
    if "weapon2" in varDict:
      if varDict["weapon2"]:
        self.cannon = 1
    if (self.triggerWorkaround):
      try:
        pygame.event.pump()
        if ("type" in varDict) and (varDict["type"] in ("f4u-1c",)) and (self.joy.get_button(joytrigger)):
          self.cannon = 1
      except:
        self.triggerWorkaround = False
      
    if "H, m"  in varDict:
      self.alt = varDict["H, m"]
    if "RPM 1" in varDict:
      self.rpm = varDict["RPM 1"]
    if "gear, %" in varDict:
      self.gear = varDict["gear, %"] / 100.0
    if "flaps, %" in varDict:
      self.flaps = varDict["flaps, %"] / 100.0
    if "IAS, km/h" in varDict:
      self.speed = varDict["IAS, km/h"]
    if "AoA, deg" in varDict:
      self.aoa = varDict["AoA, deg"]
    if "vario" in varDict:
      self.vario = varDict["vario"]

    self.lastPacket = time.time()

  
  def recvData(self):

    try:
      response =  urllib.request.urlopen(self.urls, timeout = 0.5)
      content = response.read()
      varDict = json.loads(content)
      response =  urllib.request.urlopen(self.urli, timeout = 0.5)
      content = response.read()
      varDict.update(json.loads(content))
      
      self.parseTelem(varDict)
      
    except:
      log.exception('')

  def start(self):
    self.s = None
    self.motionTick = None
    self.acc = None
    self.lastAccel = None
    
    if (self.triggerWorkaround):
      try:
        if not pygame.get_init():
          pygame.init()
        if not pygame.joystick.get_init():
          pygame.joystick.init()
        self.joy = pygame.joystick.Joystick(joyNumber)
      except:
        self.triggerWorkaround = False

    errCode = 'valid'
    try:
      try:
        baseBHap.BaseSim.start(self)
      except:
        msg = 'Error conecting. Is bHaptics player app running?\n'
        log.exception(msg)
        return (msg, 'error')
      
      msg = "WThBHap started\n"
    except Exception as excp:
      log.exception('')
      errCode = 'error'
      msg = (str(excp)+'\n'+traceback.format_exc())
    return (msg, errCode)

  def stop(self):
    if (self.triggerWorkaround):
      #pygame.joystick.quit()
      #pygame.quit()
      pass
  
    baseBHap.BaseSim.stop(self)
    if self.s:
      self.s.close()
      self.s = None
    return ("WThBHap stopped\n", "valid")

if __name__ == "__main__": 

  sim = Sim()
  print(sim.start())
  while True:
    sim.runCycle()
    time.sleep(0.001)
  sim.stop()
