import socket
import time
import errno
import struct
import math
import os
import re


serverAddressPort   = ("127.0.0.1", 4125)
bufferSize          = 10240

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.bind(serverAddressPort)
s.setblocking(0)

refloatList = re.compile("-?\d+\.\d+")

counter = 0
while True:
  try:
    counter += 1
    msg = s.recvfrom(bufferSize)
    floatList = refloatList.findall(msg[0].decode('ascii'))
    if (counter % 5) == 0:
      os.system('cls')
      for value in floatList:
        print  (value)
  except socket.error as e:
    err = e.args[0]
    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
        pass
        time.sleep(0.001)
    else:
        # a "real" error occurred
        print (e)
