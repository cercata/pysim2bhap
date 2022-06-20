import socket
import time
import errno
import struct
import math
import os


serverAddressPort   = ("127.0.0.1", 20777)
bufferSize          = 512

structDR2_0   = struct.Struct("<"+"f"*17)
structDR2_1   = struct.Struct("<"+"f"*38)
structDR2_3   = struct.Struct("<"+"f"*66)

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.bind(serverAddressPort)
s.setblocking(0)


counter = 0
timeSim = 0.0
speed = 0.0
vlfwD = 0.0
vrfwD = 0.0
vlrwD = 0.0
vrrwD = 0.0
vlfw = 0.0
vrfw = 0.0
vlrw = 0.0
vrrw = 0.0

while True:
  try:
    counter += 1
    msg = s.recvfrom(bufferSize)
    #print (len(msg[0]))
    if len(msg[0]) == 264:
      #floatList = refloatList.findall(msg[0].decode('ascii'))
      floatList = structDR2_3.unpack(msg[0][0:264])
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
      if timeDelta:      
        vlfwD = (float(floatList[19]) - vlfw) / timeDelta
        vrfwD = (float(floatList[20]) - vrfw) / timeDelta
        vlrwD = (float(floatList[17]) - vlrw) / timeDelta
        vrrwD = (float(floatList[18]) - vrrw) / timeDelta   
      vlfw = float(floatList[19])
      vrfw = float(floatList[20])
      vlrw = float(floatList[17])
      vrrw = float(floatList[18])    
      rpm = floatList[37]
      maxrpm = floatList[63]
      if (counter % 5) == 0:
        os.system('cls')
        print (f"time:       {timeSim}")
        print (f"delta:      {timeDelta}")
        print (f"speed:      {speed}")
        print (f"accel:      {accel}")
        print (f"lonGForce:  {lonGForce}")
        print (f"latGForce:  {latGForce}")
        print (f"gear:       {gear}")
        print (f"vlfw:       {vlfw}")
        print (f"vrfw:       {vrfw}")
        print (f"vlrw:       {vlrw}")
        print (f"vrrw:       {vrrw}")
        print (f"rpm:        {rpm}")
        print (f"maxrpm:     {maxrpm}")
        #for value in floatList:
        #  print  (value)
    if len(msg[0]) == 68:
      floatList = structDR2_0.unpack(msg[0][0:68])
      if (counter % 5) == 0:
        os.system('cls')
        for i in range(17):
          print (f"{i}:  {floatList[i]}")
  except socket.error as e:
    err = e.args[0]
    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
        pass
        time.sleep(0.001)
    else:
        # a "real" error occurred
        print (e)
