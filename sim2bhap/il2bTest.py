import socket
import time
import errno
import struct
import math
import os

structFloat   = struct.Struct("<f")
structLong    = struct.Struct("<l")
structShort   = struct.Struct("<h")
structByte    = struct.Struct("<b")

def findFloats(buff):
  floatList = []
  floatList2 = []
  for i in range(10, len(buff)-3):
    (value,) = structFloat.unpack(buff[i:i+4])
    if ((abs(value) < 300000) and (abs(value) > 0.01)) or (value == 0):
      floatList.append([i, value, buff[i:i+4].hex()])
    floatList2.append([i, value, buff[i:i+4].hex()])
  return (floatList, floatList2)

structMotion = struct.Struct("<LLfffffffff")
structTelem131  = struct.Struct("<Lbbbbb"+"f"*30+"bb")
structTelem147  = struct.Struct("<LHL"+"B"*137)

serverAddressPort   = ("127.0.0.1", 29373)
bufferSize          = 10240

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.bind(serverAddressPort)
s.setblocking(0)

prevMsg = None
counter = 0
diffThreshold = 100
lenTelem = 131
#lenTelem = 147
diffDict = {}
posToPrint = [14, 21, 28, 35, 42, 49, 53, 57, 64, 68, 72, 79, 86, 93, 97, 101, 108, 112, 119, 126]
#posToPrint = [14, 18, 25, 29, 36, 43, 47, 54, 58, 65, 69, 73, 80, 84, 88, 95, 102, 109, 113, 117, 124, 128, 135, 143]

posToPrintL= [0, 6]
posToPrintS= [4, 10, 11, 18, 25, 32, 39, 46, 61, 76, 83, 90, 105, 116, 123]
posToPrintB= [10, 13, 20, 27, 34, 41, 48, 63, 78, 85, 92, 107, 118, 125, 130]
for i in range(10, lenTelem):
  diffDict[i] = 0
while True:
  try:
    msg = s.recvfrom(bufferSize)
    dataLen = len(msg[0])
    if dataLen == 44:
      listMotion = structMotion.unpack(msg[0])
      msg = "Motion {}".format(str(listMotion))
      print("Acel: {} {} {}".format(listMotion[8],listMotion[9],listMotion[10]))
    elif dataLen >= lenTelem:
      counter+= 1
      #os.system('cls')
      if False:
        fl = findFloats(msg[0])
        print("")
        print (fl[0])
        print (fl[1])
      #listTelem = structTelem147.unpack(msg[0])
      #print (listTelem[0:3])
      if False:
        if prevMsg is not None:
          for i in range(10, len(msg[0])):
            if msg[0][i] != prevMsg[0][i]:
              if counter < diffThreshold:
                diffDict[i] += 1
              else:
                if diffDict[i] <= 0:
                  #print("Pos {} changed from {} to {}".format(i, prevMsg[0][i], msg[0][i]))
                  pass
                else:
                  diffDict[i] += 1
        prevMsg = msg
      if False:
       if counter % 5 == 3:
         os.system('cls')
         for pos in posToPrint:
           #(value,) = structFloat.unpack(prevMsg[0][pos:pos+4])
           (value2,) = structFloat.unpack(msg[0][pos:pos+4])
           print ("  Pos {}: {} ".format(pos, value2))
         (g1,) = structFloat.unpack(msg[0][101:105])
         (g2,) = structFloat.unpack(msg[0][93:97])
         (g3,) = structFloat.unpack(msg[0][97:101])
         g4 = math.sqrt((g1/9.8)*(g1/9.8)+(g2/9.8)*(g2/9.8))
         g  = math.sqrt((g3/9.8)*(g3/9.8)+(g4/9.8)*(g4/9.8))
         print ("  G : {} ".format(g))
         for pos in posToPrintL:
           (value,) = structLong.unpack(msg[0][pos:pos+4])
           print ("  Pos {}: {} ".format(pos, value))
         for pos in posToPrintS:
           (value,) = structShort.unpack(msg[0][pos:pos+2])
           print ("  Pos {}: {} ".format(pos, value))
         for pos in posToPrintB:
           print ("  Pos {}: {} ".format(pos, msg[0][pos]))
      if True:
        if len(msg[0]) > lenTelem:
          print (" Packet len {} -> EndCode {}".format(len(msg[0]), msg[0][130]))
    time.sleep(0.001)
  except socket.error as e:
    err = e.args[0]
    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
        pass
        time.sleep(0.001)
    else:
        # a "real" error occurred
        print (e)
