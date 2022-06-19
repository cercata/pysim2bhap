import socket
import time
import errno
import struct
import math
import os


serverAddressPort   = ("127.0.0.1", 20777)
bufferSize          = 512

structDR2   = struct.Struct("<"+"f"*66)


s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.bind(serverAddressPort)
s.setblocking(0)


counter = 0
timeSim = 0.0
speed = 0.0

while True:
  try:
    counter += 1
    msg = s.recvfrom(bufferSize)
    #print (len(msg[0]))
    #floatList = refloatList.findall(msg[0].decode('ascii'))
    floatList = structDR2.unpack(msg[0][0:264])
    timeDelta = floatList[0] - timeSim
    timeSim = floatList[0]
    speedDelta = floatList[7] - speed
    if (timeDelta):
      accel = speedDelta / timeDelta / 9.8
    else:
      accel = 0.0
    speed = floatList[7]
    gear = floatList[33]
    latGForce = floatList[34]
    lonGForce = floatList[35]
    rpm = floatList[37]
    maxrpm = floatList[63]
    val64 = floatList[64]
    val65 = floatList[65]
    if (counter % 5) == 0:
      os.system('cls')
      print (f"time:       {timeSim}")
      print (f"delta:      {timeDelta}")
      print (f"speed:      {speed}")
      print (f"accel:      {accel}")
      print (f"lonGForce:  {lonGForce}")
      print (f"latGForce:  {latGForce}")
      print (f"gear:       {gear}")
      print (f"rpm:        {rpm}")
      print (f"maxrpm:     {maxrpm}")
      print (f"val64:      {val64}")
      print (f"val65:      {val65}")
      #for value in floatList:
      #  print  (value)
  except socket.error as e:
    err = e.args[0]
    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
        pass
        time.sleep(0.001)
    else:
        # a "real" error occurred
        print (e)
